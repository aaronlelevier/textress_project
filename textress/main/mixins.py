from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.views.generic.base import View, ContextMixin
from django.views.generic.edit import FormMixin
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.forms.models import model_to_dict

from braces.views import GroupRequiredMixin

from main.models import Hotel
from contact.models import Newsletter
from contact.forms import NewsletterForm
from payment.mixins import HotelContextMixin


class HotelMixin(ContextMixin, View):
    '''Adds the User's Hotel.'''

    def dispatch(self, request, *args, **kwargs):
        try:
            self.hotel = request.user.profile.hotel
        except AttributeError:
            return Http404

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
            raise PermissionDenied

        self.hotel = self.request.user.profile.hotel

        return super(UserOnlyMixin, self).dispatch(request, *args, **kwargs)


class HotelUsersOnlyMixin(HotelContextMixin, GroupRequiredMixin, View):
    '''
    Users must belong to the Hotel of the User record that they are requesting.

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
            raise PermissionDenied

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
            raise PermissionDenied

        return super(MyHotelOnlyMixin, self).dispatch(request, *args, **kwargs)


### REGISTRATION MIXINS ###

class RegistrationContextMixin(object):

    def get_context_data(self, **kwargs):
        context = super(RegistrationContextMixin, self).get_context_data(**kwargs)
        context['steps'] = ['User Information', 'Hotel Information', 'Plan Structure',
            'Payment', 'Payment Success']
        return context