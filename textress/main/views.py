from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.models import User, Group
from django.views.generic import CreateView, DetailView, UpdateView
from django.views.generic.base import View, TemplateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect

from rest_framework.response import Response
from rest_framework import permissions, generics
from braces.views import (LoginRequiredMixin, GroupRequiredMixin,
     SetHeadlineMixin, FormValidMessageMixin, FormInvalidMessageMixin)

from concierge.permissions import (IsHotelObject, IsManagerOrAdmin, IsHotelUser,
    IsHotelOfUser)
from main.models import Hotel, UserProfile, Subaccount, viewable_user_fields_dict
from main.forms import UserCreateForm, HotelCreateForm, UserUpdateForm, DeleteUserForm
from main.mixins import (UserOnlyMixin, UserListContextMixin,
    MyHotelOnlyMixin, RegistrationContextMixin, HotelUserMixin, HotelContextMixin,
    UsersHotelMatchesHotelMixin, UsersHotelMatchesUsersHotelMixin)
from main.serializers import UserSerializer, HotelSerializer
from utils import dj_messages, login_messages, EmptyForm, DeleteButtonMixin


### Hotel ###

class HotelUpdateView(UsersHotelMatchesHotelMixin, GroupRequiredMixin, SetHeadlineMixin, 
    FormValidMessageMixin, UpdateView):
    '''
    Will use permissions in templating to only expose this View to Hotel Admins.
    Also, view URL is only accessible by Admins.
    '''
    group_required = ["hotel_admin"]
    headline = "Update Hotel Info"
    model = Hotel
    form_class = HotelCreateForm
    template_name = 'cpanel/form.html'
    form_valid_message = dj_messages['hotel_updated']

    def get_success_url(self):
        return reverse('main:user_detail', kwargs={'pk': self.request.user.pk})

    def get_form_kwargs(self):
        "Set Hotel as a form attr."
        kwargs = super(HotelUpdateView, self).get_form_kwargs()
        kwargs['hotel'] = self.object
        return kwargs


### REGISTRATION VIEWS ###

class RegisterAdminBaseView(RegistrationContextMixin, View):
    '''
    BaseView for Registration Step # 1, and will change based on 
    Create / Update.
    '''
    model = User
    form_class = UserCreateForm
    template_name = 'frontend/register/register.html'
    success_url = reverse_lazy('main:register_step2')
    authenticated_redirect_url = settings.VERIFY_LOGOUT_URL

    def get_context_data(self, **kwargs):
        context = super(RegisterAdminBaseView, self).get_context_data(**kwargs)
        context['step_number'] = 0
        context['step'] = context['steps'][context['step_number']]
        return context


class RegisterAdminCreateView(RegisterAdminBaseView, CreateView):
    '''
    Step #1 of Registration - CreateView

    Purpose:
        - Create a new User
        - Add them to the "hotel_admin" Group
        - Log in User

    If Admin User already exists, re-route to the UpdateView.
    '''
    def dispatch(self, request, *args, **kwargs):
        try:
            user = User.objects.get(pk=self.request.user.pk)
        except (AttributeError, ObjectDoesNotExist):
            return super(RegisterAdminCreateView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('main:register_step1_update',
                kwargs={'pk': user.pk}))

    def form_valid(self, form):
        # Call super-override so ``User`` object is available
        super(RegisterAdminCreateView, self).form_valid(form) 
        cd = form.cleaned_data

        # Add User to "Admin" Group
        user = User.objects.get(username=cd['username'])
        group = Group.objects.get(name='hotel_admin')
        user.groups.add(group)
        user.save()

        # Login
        user = auth.authenticate(username=cd['username'], password=cd['password1'])
        if not user:
            raise forms.ValidationError(login_messages['no_match'])
        auth.login(self.request, user)
        messages.info(self.request, login_messages['now_logged_in'])

        return HttpResponseRedirect(self.get_success_url())


class RegisterAdminUpdateView(GroupRequiredMixin, RegisterAdminBaseView,
    UserOnlyMixin, UpdateView):
    '''
    For Registration Update of Admin User info only.
    '''
    group_required = ["hotel_admin"]
    model = User
    form_class = UserUpdateForm


class RegisterHotelBaseView(GroupRequiredMixin, RegistrationContextMixin, View):
    '''
    BaseView to support Hotel Create / Update Views for Registration.
    '''
    group_required = ["hotel_admin"]
    model = Hotel
    form_class = HotelCreateForm
    template_name = 'frontend/register/register.html'
    success_url = reverse_lazy('register_step3')

    def get_context_data(self, **kwargs):
        context = super(RegisterHotelBaseView, self).get_context_data(**kwargs)
        context['step_number'] = 1
        context['step'] = context['steps'][context['step_number']]
        return context

    def get_form_kwargs(self):
        "Set Hotel as a form attr."
        kwargs = super(RegisterHotelBaseView, self).get_form_kwargs()
        kwargs['hotel'] = self.object
        return kwargs


class RegisterHotelCreateView(RegisterHotelBaseView, CreateView):
    """
    Step #2 of Registration

    Purpose:
        - Create Hotel
        - Set Hotel to the User's UserProfile Hotel
        - Set User's ID as the Hotel Admin ID of the Hotel
    """
    def dispatch(self, request, *args, **kwargs):
        try:
            hotel = Hotel.objects.get(pk=self.request.user.profile.hotel.pk)
        except (AttributeError, ObjectDoesNotExist):
            return super(RegisterHotelCreateView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('main:register_step2_update',
                kwargs={'pk': hotel.pk}))

    def form_valid(self, form):
        # Call super-override so ``Hotel`` object is available
        super(RegisterHotelCreateView, self).form_valid(form)
        # User is now this Hotel's Admin
        self.object.set_admin_id(user=self.request.user)
        # Link Hotel and User
        self.request.user.profile.update_hotel(hotel=self.object)

        return HttpResponseRedirect(self.get_success_url())


class RegisterHotelUpdateView(MyHotelOnlyMixin, RegisterHotelBaseView, UpdateView):
    pass


##############
# MY PROFILE #
##############

class UserDetailView(LoginRequiredMixin, SetHeadlineMixin, UserOnlyMixin, DetailView):
    '''User's DetailView of themself.'''

    headline = "My Profile"
    model = User
    template_name = 'main/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context['user_dict'] = viewable_user_fields_dict(self.request.user)
        context['hotel'] = self.hotel
        return context


class UserUpdateView(SetHeadlineMixin, FormValidMessageMixin, LoginRequiredMixin,
    UserOnlyMixin, UpdateView):
    '''User's UpdateView of themself.'''

    headline = "Update Profile"
    model = User
    form_class = UserUpdateForm
    template_name = 'cpanel/form.html'
    form_valid_message = dj_messages['profile_updated']

    def get_success_url(self):
        return reverse('main:user_detail', kwargs={'pk': self.request.user.pk})


################
# MANAGE USERS #
################

class MgrUserListView(SetHeadlineMixin, GroupRequiredMixin, HotelUserMixin, TemplateView):
    '''
    :Angular View:
        So can be a TemplateView since the Object List is 
        generated from a REST Endpoint.

    List all Users for a Hotel, except for the Admin, for the 
    Admin or Managers to `view/add/edit/delete.
    '''
    headline = 'User List'
    group_required = ["hotel_admin", "hotel_manager"]
    template_name = 'main/user_list.html'


class UserCreateView(SetHeadlineMixin, HotelUserMixin, LoginRequiredMixin, GroupRequiredMixin,
    UserListContextMixin, CreateView):
    """
    Create a Normal Hotel User w/ no permissions.
    Auto-add all created Users to the Group of the Hotel
    """

    headline = "Add a User"
    group_required = ["hotel_admin", "hotel_manager"]
    model = User
    form_class = UserCreateForm
    template_name = 'cpanel/form.html'
    success_url = reverse_lazy('main:manage_user_list')

    def form_valid(self, form):
        super(UserCreateView, self).form_valid(form)

        cd = form.cleaned_data
        self.newuser = User.objects.get(username=cd['username'])
        self.newuser.profile.update_hotel(hotel=self.request.user.profile.hotel)
        messages.info(self.request, 'User created')

        return HttpResponseRedirect(self.get_success_url())


class ManagerCreateView(UserCreateView):
    "Create Manager Hotel User w/ Manager Permissions"

    headline = "Add a Manager"

    def form_valid(self, form):
        super(ManagerCreateView, self).form_valid(form)

        hotel_admin = Group.objects.get(name='hotel_manager')
        self.newuser.groups.add(hotel_admin)
        self.newuser.save()

        return HttpResponseRedirect(self.get_success_url())


class MgrUserDetailView(LoginRequiredMixin, SetHeadlineMixin, UsersHotelMatchesUsersHotelMixin,
    UserListContextMixin, DetailView):
    '''User's DetailView of themself.'''

    headline = "User Profile"
    model = User
    template_name = 'main/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super(MgrUserDetailView, self).get_context_data(**kwargs)
        context['user_dict'] = viewable_user_fields_dict(self.object)
        context['hotel'] = self.hotel
        return context


class MgrUserUpdateView(UsersHotelMatchesUsersHotelMixin, SetHeadlineMixin,
    UserListContextMixin, UpdateView):
    '''
    Manager/Admin view of Users.
    '''
    headline = "Update Profile"
    model = User
    form_class = UserUpdateForm
    template_name = 'cpanel/form.html'

    def get_success_url(self):
        return reverse('main:manage_user_list')


class MgrUserDeleteView(SetHeadlineMixin, DeleteButtonMixin, UsersHotelMatchesUsersHotelMixin,
    GroupRequiredMixin, UserListContextMixin, FormInvalidMessageMixin, UpdateView):
    '''
    A Mgr+ can delete any User for their Hotel except the AdminUser.
    '''
    headline = "User Delete View"
    groups = ['hotel_admin', 'hotel_manager']
    model = UserProfile
    form_class = DeleteUserForm
    template_name = 'cpanel/form.html'
    success_url = reverse_lazy('main:manage_user_list')
    form_invalid_message = dj_messages['delete_admin_fail']

    def get_form_kwargs(self):
        kwargs = super(MgrUserDeleteView, self).get_form_kwargs()
        kwargs['user'] = self.object.user
        return kwargs

    def form_valid(self, form):
        self.object.hide()
        return super(MgrUserDeleteView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(MgrUserDeleteView, self).get_context_data(**kwargs)
        context['addit_info'] = '''
            <h4>Are you sure that you want to delete <strong>{}</strong>?</h4>
            '''.format(self.object.user.username)
        return context


##################
# REST API VIEWS #
##################

### USER ###

class UserListAPIView(generics.ListAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsManagerOrAdmin)

    def list(self, request):
        users = User.objects.filter(profile__hotel=request.user.profile.hotel)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserRetrieveAPIView(generics.RetrieveAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsManagerOrAdmin, IsHotelUser)


### HOTEL ###

class HotelRetrieveAPIView(generics.RetrieveAPIView):

    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = (permissions.IsAuthenticated, IsManagerOrAdmin, IsHotelOfUser)