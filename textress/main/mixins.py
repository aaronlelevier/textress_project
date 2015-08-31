from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.views.generic.base import View
from django.http import Http404
from django.core.exceptions import PermissionDenied

from braces.views import GroupRequiredMixin

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
    '''
    def dispatch(self, *args, **kwargs):
        try:
            self.hotel = self.request.user.profile.hotel
        except AttributeError:
            messages.warning(self.request, dj_messages['no_hotel'])
            raise PermissionDenied

        # TODO: Redirect to an alert page that funds need to be added
        if self.hotel and not self.hotel.active:
            messages.warning(self.request, dj_messages['hotel_not_active'])
            raise Http404
            
        return super(HotelUserMixin, self).dispatch(*args, **kwargs)


class AdminOnlyMixin(GroupRequiredMixin, HotelContextMixin, View):
    '''
    Only the Admin for the Hotel can access this page when using this mixin.
    '''
    group_required = "hotel_admin"

    def dispatch(self, *args, **kwargs):
        self.hotel = self.request.user.profile.hotel
        admin_hotel = get_object_or_404(Hotel, admin_id=self.request.user.id)
        if admin_hotel != self.hotel:
            raise Http404
        return super(AdminOnlyMixin, self).dispatch(*args, **kwargs)


### REGISTRATION MIXINS ###

class RegistrationContextMixin(object):

    def get_context_data(self, **kwargs):
        context = super(RegistrationContextMixin, self).get_context_data(**kwargs)
        context['steps'] = ['User Information', 'Hotel Information', 'Plan Structure',
            'Payment', 'Payment Success']
        return context