from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.models import User, Group
from django.shortcuts import render, get_object_or_404
from django.views.generic import (CreateView, FormView, DetailView,
    ListView, UpdateView, DeleteView)
from django.views.generic.base import View, ContextMixin, TemplateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext

from braces.views import (LoginRequiredMixin, PermissionRequiredMixin,
    GroupRequiredMixin, AnonymousRequiredMixin, SetHeadlineMixin)

from main.models import Hotel, UserProfile, Subaccount
from main.forms import UserCreateForm, HotelCreateForm, UserUpdateForm
from main.mixins import (HotelMixin, UserOnlyMixin, HotelUsersOnlyMixin,
    RegistrationContextMixin)
from account.helpers import add_group
from contact.mixins import NewsletterMixin, TwoFormMixin
from account.helpers import login_messages
from payment.mixins import HotelUserMixin, HotelContextMixin


### Hotel ###

class HotelUpdateView(HotelUsersOnlyMixin, GroupRequiredMixin, SetHeadlineMixin, UpdateView):
    '''
    Will use permissions in templating to only expose this View to Hotel Admins.
    Also, view URL is only accessible by Admins.
    '''
    group_required = ["hotel_admin"]
    headline = "Update Hotel Info"
    model = Hotel
    form_class = HotelCreateForm
    fields = ['name', 'address_phone', 'address_line1', 'address_line2',
        'address_city', 'address_state', 'address_zip']
    template_name = 'cpanel/form.html'

    def get_success_url(self):
        return reverse('account')




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
            return HttpResponseRedirect(reverse('main:register_step1_update', kwargs={'pk': user.pk}))

    def form_valid(self, form):
        # Call super-override so ``User`` object is available
        super(RegisterAdminCreateView, self).form_valid(form) 
        cd = form.cleaned_data

        # Add User to "Admin" Group
        user = add_group(user=User.objects.get(username=cd['username']),
            group='hotel_admin')

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
    For Registration Update User info only.
    '''
    group_required = ["hotel_admin"]
    model = User
    form_class = UserUpdateForm
    fields = ['first_name', 'last_name', 'email']


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
            return HttpResponseRedirect(reverse('main:register_step2_update', kwargs={'pk': hotel.pk}))

    def form_valid(self, form):
        # Call super-override so ``Hotel`` object is available
        super(RegisterHotelCreateView, self).form_valid(form)
        # User is now this Hotel's Admin
        self.object.set_admin_id(user=self.request.user)
        # Link Hotel and User
        self.request.user.profile.update_hotel(hotel=self.object)

        return HttpResponseRedirect(self.get_success_url())


class RegisterHotelUpdateView(HotelUsersOnlyMixin, RegisterHotelBaseView, UpdateView):
    pass


#########
# USERS #
#########

class UserDetailView(UserOnlyMixin, DetailView):
    '''User's DetailView of themself.'''

    model = User
    template_name = 'detail_view.html'


class UserUpdateView(SetHeadlineMixin, UserOnlyMixin, UpdateView):
    '''User's UpdateView of themself.'''
    headline = "Update Profile"
    model = User
    form_class = UserUpdateForm
    fields = ['first_name', 'last_name', 'email']
    template_name = 'cpanel/form.html'

    def get_success_url(self):
        return reverse('account')


################
# MANAGE USERS #
################

class MgrUserListView(GroupRequiredMixin, HotelUserMixin, ListView):
    '''List all Users for a Hotel, except for the Admin, for the 
    Admin or Managers to `view/add/edit/delete.'''

    group_required = ["hotel_admin", "hotel_manager"]
    template_name = 'list_view.html'
    
    def get_queryset(self):
        return (User.objects.select_related('userprofile')
                            .filter(profile__hotel=self.hotel)
                            .exclude(pk=self.hotel.admin_id))


class MgrUserDetailView(HotelUsersOnlyMixin, DetailView):
    '''Admin or Managers detail view of the User.'''

    group_required = ["hotel_admin", "hotel_manager"]
    model = User
    template_name = 'detail_view.html'


class UserCreateView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    "Create a Normal Hotel User w/ no permissions."

    group_required = ["hotel_admin", "hotel_manager"]
    model = User
    form_class = UserCreateForm
    template_name = 'main/hotel_form.html'
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

    def form_valid(self, form):
        super(ManagerCreateView, self).form_valid(form)

        hotel_admin = Group.objects.get(name='hotel_manager')
        self.newuser.groups.add(hotel_admin)
        self.newuser.save()

        return HttpResponseRedirect(self.get_success_url())


class MgrUserUpdateView(HotelUsersOnlyMixin, UpdateView):
    '''User's UpdateView of themself.

    TODO: 
        -Add a FormSet, so that Mgrs' can in the same view adjust
            Group Status to "hotel_manager" or take it away.
        - also be able to view Group.
    '''
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'account/account_form.html'

    def get_success_url(self):
        return reverse('main:manage_user_detail', kwargs={'pk': self.object.pk})


class MgrUserDeleteView(HotelUsersOnlyMixin, DeleteView):
    '''A Mgr can delete any User for their Hotel except the AdminUser.

    TODO: This should be a "hide" not a "delete"
        add django-braces - GroupRequiredMixin
    '''

    model = User
    template_name = 'account/account_form.html'
    success_url = reverse_lazy('main:manage_user_list')