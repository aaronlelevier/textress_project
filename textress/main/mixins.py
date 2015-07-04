from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.views.generic.base import View, ContextMixin
from django.views.generic.edit import FormMixin
from django.http import Http404
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.forms.models import model_to_dict

from braces.views import GroupRequiredMixin

from main.models import Hotel
from contact.models import Newsletter
from contact.forms import NewsletterForm
from payment.mixins import HotelContextMixin


class UserContextDataMixin(object):
    '''
    Display all fields of user into to start.
    '''
    def get_context_data(self, **kwargs):
        context = super(UserContextDataMixin, self).get_context_data(**kwargs)
        # populate user in the context w/o the password key
        user_dict = model_to_dict(self.request.user)
        user_dict.pop("password", None)
        context['user_dict'] = user_dict
        return context


class HotelContextDataMixin(object):
    '''
    Display all Hotel fields.
    '''
    def get_context_data(self, **kwargs):
        context = super(HotelContextDataMixin, self).get_context_data(**kwargs)

        # get the Hotel object for the User
        try:
            hotel_dict = model_to_dict(self.request.user.profile.hotel)
        except KeyError:
            raise Http404
        else:
            context['hotel_dict'] = hotel_dict
            return context


class NewsletterMixin(FormMixin):

    form_class = NewsletterForm
    # will most likely be overwritten in the inheriting view
    success_url = reverse_lazy('main:index')

    def get_context_data(self, **kwargs):
        context = super(NewsletterMixin, self).get_context_data(**kwargs)
        context['nl_form'] = self.get_form_class()
        return context


class HotelMixin(ContextMixin, View):
    '''
    TODO: remove this view b/c replaced by other Hotel Mixins ??
    '''

    def dispatch(self, request, *args, **kwargs):
        self.hotel = request.user.profile.hotel
        return super(HotelMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HotelMixin, self).get_context_data(**kwargs)
        context['hotel'] = self.hotel
        return context


### USER MIXINS ###

class UserOnlyMixin(HotelContextMixin):
    '''Only the User themself can Access this View, and the
    related Objects to the User.'''

    def dispatch(self, request, *args, **kwargs):
        pk = int(kwargs['pk'])
        if request.user.pk != pk:
            raise Http404

        self.hotel = self.request.user.profile.hotel

        return super(UserOnlyMixin, self).dispatch(request, *args, **kwargs)


class HotelUsersOnlyMixin(HotelContextMixin, GroupRequiredMixin, View):
    '''
    Users must belong to the Hotel of the requesting User.

    Requesting User must be a: Admin/Manager
    '''
    group_required = ["hotel_admin", "hotel_manager"]

    def dispatch(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs['pk']) 
        # check that this is the User's Hotel before dispatching
        try:
            self.hotel = user.profile.hotel
            user_hotel = self.hotel == self.request.user.profile.hotel
        except AttributeError:
            user_hotel = None

        if not user_hotel:
            raise Http404

        return super(HotelUsersOnlyMixin, self).dispatch(request, *args, **kwargs)


class MyHotelOnlyMixin(HotelContextMixin, GroupRequiredMixin, View):
    '''
    Hotel Obj. must be the User's Hotel.
    '''
    group_required = ["hotel_admin", "hotel_manager"]

    def dispatch(self, request, *args, **kwargs):
        self.hotel = get_object_or_404(Hotel, pk=kwargs['pk']) 
        
        # check that this is the User's Hotel before dispatching
        try:
            user_hotel = self.hotel == self.request.user.profile.hotel
        except AttributeError:
            user_hotel = None

        if not user_hotel:
            raise Http404

        return super(MyHotelOnlyMixin, self).dispatch(request, *args, **kwargs)


class RegistrationContextMixin(object):

    def get_context_data(self, **kwargs):
        context = super(RegistrationContextMixin, self).get_context_data(**kwargs)
        context['steps'] = ['User Information', 'Hotel Information', 'Plan Structure',
            'Payment', 'Success']
        return context