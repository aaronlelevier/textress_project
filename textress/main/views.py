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
from main.mixins import (HotelMixin, UserOnlyMixin, HotelUsersOnlyMixin,
    RegistrationContextMixin)
from account.helpers import add_group
from contact.mixins import NewsletterMixin, TwoFormMixin
from account.helpers import login_messages
from payment.mixins import HotelUserMixin, HotelContextMixin


### BUSINESS VIEWS ###

class IndexView(NewsletterMixin, FormView):

    template_name = 'frontend/index.html'


class TermsNCondView(TemplateView):
    template_name = 'frontend/terms_n_cond.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = "Textress"
        context['LLC'] = "Aronysidoro LLC."
        return context


### TODO: What is this view being used for? ###

class HotelDetailView(HotelMixin, DetailView):

    model = Hotel


### REGISTRATION VIEWS ###

class AdminCreateView(RegistrationContextMixin, CreateView):
    """
    Step #1 of Registration

    Purpose:
        - Create a new User
        - Add them to the "hotel_admin" Group
        - Log in User
    """
    model = User
    form_class = UserCreateForm
    template_name = 'frontend/register.html'
    success_url = reverse_lazy('main:register_step2')
    authenticated_redirect_url = settings.VERIFY_LOGOUT_URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['step_number'] = 0
        context['step'] = context['steps'][context['step_number']]
        return context

    def form_valid(self, form):
        # Call super() so ``User`` object is available
        super().form_valid(form) 
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


class HotelCreateView(LoginRequiredMixin, RegistrationContextMixin, CreateView):
    """
    Step #2 of Registration

    Purpose:
        - Create Hotel
        - Set Hotel to the User's UserProfile Hotel
        - Set User's ID as the Hotel Admin ID of the Hotel
    """
    model = Hotel
    form_class = HotelCreateForm
    template_name = 'frontend/register.html'
    success_url = reverse_lazy('register_step3')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['step_number'] = 1
        context['step'] = context['steps'][context['step_number']]
        return context

    def form_valid(self, form):
        # Call super() so ``Hotel`` object is available
        super().form_valid(form)

        # User is now this Hotel's Admin
        self.object.set_admin_id(user=self.request.user)
        # Link Hotel and User
        self.request.user.profile.update_hotel(hotel=self.object)

        return HttpResponseRedirect(self.get_success_url())


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







