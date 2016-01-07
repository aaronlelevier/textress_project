from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.base import View

from braces.views import GroupRequiredMixin

from account.models import AcctCost
from main.helpers import get_user_hotel
from main.models import Hotel
from utils import dj_messages, mixins


class UserListContextMixin(mixins.BreadcrumbBaseMixin):

    def __init__(self):
        self.clip_icon = 'clip-users-2'
        self.url = reverse('main:manage_user_list')
        self.url_name = 'User List'


class HotelContextMixin(object):
    '''Add Hotel Obj to Context.'''
    
    def get_context_data(self, **kwargs):
        context = super(HotelContextMixin, self).get_context_data(**kwargs)
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

from braces.views._access import AccessMixin

class UsersHotelMatchesHotelMixin(HotelContextMixin, AccessMixin):
    '''
    The requesting Hotel must match the User's Hotel.
    '''

    def dispatch(self, request, *args, **kwargs):
        self.hotel = get_object_or_404(Hotel, pk=kwargs.get('pk', None))

        try:
            user_hotel = self.request.user.profile.hotel
        except AttributeError:
            return self.handle_no_permission(request)
        else:
            if self.hotel != user_hotel:
                return self.handle_no_permission(request)

        return super(UsersHotelMatchesHotelMixin, self).dispatch(
            request, *args, **kwargs)


class UsersHotelMatchesUsersHotelMixin(GroupRequiredMixin, HotelContextMixin, View):
    '''
    The requested User's Hotel must match the User's Hotel.
    '''
    group_required = ["hotel_admin", "hotel_manager"]

    def dispatch(self, request, *args, **kwargs):
        requested_user = get_object_or_404(User, pk=kwargs.get('pk', None))

        try:
            self.hotel = self.request.user.profile.hotel
            requested_user_hotel = requested_user.profile.hotel
        except AttributeError:
            raise PermissionDenied
        else:
            if self.hotel != requested_user_hotel:
                raise PermissionDenied

        return super(UsersHotelMatchesUsersHotelMixin, self).dispatch(request, *args, **kwargs)


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


### HOTEL MIXINS ###

class HotelObjectMixin(object):
    '''
    Enforces in DetailViews where the ``object`` has a ``hotel`` Attr 
    that it belongs to the User's Hotel.
    '''
    def get(self, request, *args, **kwargs):
        hotel = get_user_hotel(request.user)
        self.object = self.get_object()
        
        if hotel != self.object.hotel:
            raise PermissionDenied

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class HotelUserMixin(HotelContextMixin):
    '''
    User must have belong to a Hotel, and the Hotel must be in good standing. 
    If the Hotel has no $$, then active=False.

    :LOGIN_VERIFIER:
        Makes sure all "registration" steps have been completed, and if they 
        haven't, will redirect the User accordingly.
    '''
    def dispatch(self, *args, **kwargs):
        self.hotel = self.request.user.profile.hotel

        if settings.LOGIN_VERIFIER:

            if not self.hotel:
                messages.warning(self.request, dj_messages['complete_registration'])
                return HttpResponseRedirect(reverse('main:register_step2'))
            elif not AcctCost.objects.filter(hotel=self.hotel).exists():
                messages.warning(self.request, dj_messages['complete_registration'])
                return HttpResponseRedirect(reverse('register_step3'))
            elif not self.hotel.customer:
                messages.warning(self.request, dj_messages['complete_registration'])
                return HttpResponseRedirect(reverse('payment:register_step4'))

        return super(HotelUserMixin, self).dispatch(*args, **kwargs)


class AdminOnlyMixin(GroupRequiredMixin, HotelContextMixin, View):
    '''
    Only the Admin for the Hotel can access this page when using this mixin.
    '''
    group_required = "hotel_admin"

    def dispatch(self, request, *args, **kwargs):
        self.hotel = request.user.profile.hotel

        try:
            admin_hotel = Hotel.objects.get(admin_id=request.user.id)
        except Hotel.DoesNotExist:
            admin_hotel = None

        if not admin_hotel or admin_hotel != self.hotel:
            return self.handle_no_permission(request)

        return super(AdminOnlyMixin, self).dispatch(request, *args, **kwargs)


### REGISTRATION MIXINS ###

class RegistrationContextMixin(object):

    def get_context_data(self, **kwargs):
        context = super(RegistrationContextMixin, self).get_context_data(**kwargs)
        context['steps'] = ['User Information', 'Hotel Information', 'Plan Structure',
            'Payment', 'Payment Success']
        return context
