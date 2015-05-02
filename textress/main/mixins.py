from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.views.generic.base import View, ContextMixin
from django.views.generic.edit import FormMixin
from django.http import Http404
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect

from braces.views import GroupRequiredMixin

from main.models import Hotel
from contact.models import Newsletter
from contact.forms import NewsletterForm
from payment.views import HotelUserMixin, HotelContextMixin


class NewsletterMixin(FormMixin):

    form_class = NewsletterForm
    # will most likely be overwritten in the inheriting view
    success_url = reverse_lazy('main:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nl_form'] = self.get_form_class()
        return context


class HotelMixin(ContextMixin, View):
    '''
    TODO: remove this view b/c replaced by other Hotel Mixins ??
    '''

    def dispatch(self, request, *args, **kwargs):
        self.hotel = request.user.profile.hotel
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

        self.user = (User.objects.select_related('user_profile',
                                                 'hotel')
                                                 .get(pk=pk))
        self.hotel = self.user.profile.hotel

        # TODO: add Group Object here for "hotel_manager"

        return super().dispatch(request, *args, **kwargs)


class HotelUsersOnlyMixin(HotelContextMixin, GroupRequiredMixin, View):
    '''All User Objects belong to the Hotel Obj only.

    Requred: kwargs['pk']

    TODO: Check that a normal `User` can access Views w/ this Mixin.
    '''
    group_required = ["hotel_admin", "hotel_manager"]

    def dispatch(self, request, *args, **kwargs):
        "User must be part of their Hotel, and can't be the Admin User."
        self.hotel = self.request.user.profile.hotel
        if not self.hotel:
            raise Http404
        try:
            pk = int(kwargs['pk'])
        except KeyError:
            raise Http404
        else:
            if pk not in (User.objects.filter(profile__hotel=self.hotel)
                                                .exclude(pk=self.hotel.admin_id)
                                                .values_list('id', flat=True)):
                raise Http404

        return super().dispatch(request, *args, **kwargs)


class RegistrationContextMixin(object):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['steps'] = ['User Information', 'Hotel Information', 'Plan Structure',
            'Payment', 'Pick Phone #', 'Confirmation']
        return context



