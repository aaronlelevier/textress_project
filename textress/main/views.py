from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.models import User, Group
from django.shortcuts import render, get_object_or_404
from django.views.generic import (CreateView, FormView, DetailView,
    ListView, UpdateView, DeleteView)
from django.views.generic.base import View, ContextMixin, TemplateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext

from braces.views import (LoginRequiredMixin, PermissionRequiredMixin,
    GroupRequiredMixin, AnonymousRequiredMixin)

from main.models import Hotel, UserProfile
from main.forms import UserCreateForm, HotelCreateForm
from main.mixins import HotelMixin, UserOnlyMixin, HotelUsersOnlyMixin
from contact.mixins import NewsletterMixin, TwoFormMixin
from account.helpers import login_messages
from payment.mixins import HotelUserMixin, HotelContextMixin


### BUSINESS VIEWS ###

class IndexView(NewsletterMixin, FormView):

    template_name = 'biz/index.html'


class PricingView(NewsletterMixin, FormView):

    template_name = 'biz/angular.html'


### ADMIN PREVIEW VIEWS ###

class AdminPreviewIndexView(TemplateView):
    '''Static Admin Demo View for Business Site.'''

    template_name = 'admin-preview/index.html'


class AdminPreviewBIChartsView(TemplateView):
    '''Static preview of the B.I. charts.'''

    template_name = 'admin-preview/bi-charts.html'


### TODO: What is this view being used for? ###

class HotelDetailView(HotelMixin, DetailView):

    model = Hotel


### REGISTRATION VIEWS ###

class AdminCreateView(CreateView):
    """
    Step #1 of Registration

    Purpose:
        - Create a new User
        - Add them to the "hotel_admin" Group
        - Log in User
    """
    model = User
    form_class = UserCreateForm
    template_name = 'biz/register.html'
    success_url = reverse_lazy('main:register_step2')
    authenticated_redirect_url = settings.VERIFY_LOGOUT_URL

    def form_valid(self, form):
        # Call super() so `User` object is available
        super().form_valid(form) 
        cd = form.cleaned_data

        # Add User to "Admin" Group
        hotel_admin = Group.objects.get(name='hotel_admin')
        user = User.objects.get(username=cd['username'])
        user.groups.add(hotel_admin)
        user.save()

        # Login
        user = auth.authenticate(username=cd['username'], password=cd['password1'])
        if not user:
            raise forms.ValidationError(login_messages['no_match'])
        auth.login(self.request, user)
        messages.info(self.request, login_messages['now_logged_in'])

        return HttpResponseRedirect(self.get_success_url())



class HotelCreateView(LoginRequiredMixin, CreateView):
    """
    Step #2 of Registration

    Purpose:
        - Create Hotel
        - Set Hotel to the User's UserProfile Hotel
        - Set User's ID as the Hotel Admin ID of the Hotel
    """
    model = Hotel
    form_class = HotelCreateForm

    def form_valid(self, form):
        super().form_valid(form)

        self.object.set_admin_id(user=self.request.user)

        user_profile = self.request.user.profile
        user_profile.update_hotel(hotel=self.object)

        return HttpResponseRedirect(reverse('payment:register_step3'))


#########
# USERS #
#########

class UserDetailView(UserOnlyMixin, DetailView):
    '''User's DetailView of themself.'''

    model = User
    template_name = 'detail_view.html'


class UserUpdateView(UserOnlyMixin, UpdateView):
    '''User's UpdateView of themself.'''

    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'account/account_form.html'

    def get_success_url(self):
        return reverse('main:user_detail', kwargs={'pk': self.object.pk})


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
        super().form_valid(form)

        cd = form.cleaned_data
        self.newuser = User.objects.get(username=cd['username'])
        self.newuser.profile.update_hotel(hotel=self.request.user.profile.hotel)
        messages.info(self.request, 'User created')

        return HttpResponseRedirect(self.get_success_url())


class ManagerCreateView(UserCreateView):
    "Create Manager Hotel User w/ Manager Permissions"

    def form_valid(self, form):
        super().form_valid(form)

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







