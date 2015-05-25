import calendar

from django.conf import settings
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import auth, messages
from django.contrib.auth import REDIRECT_FIELD_NAME, views as auth_views
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group, AnonymousUser

from django.views.generic import View, ListView, DetailView
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import FormView, CreateView, UpdateView, FormMixin
from django.db.models import Avg, Max, Min, Sum

from rest_framework.response import Response
from rest_framework import generics, permissions, mixins

from braces.views import (LoginRequiredMixin, PermissionRequiredMixin,
    GroupRequiredMixin, SetHeadlineMixin, AnonymousRequiredMixin)

from account.decorators import anonymous_required
from account.forms import (AuthenticationForm, CloseAccountForm,
    CloseAcctConfirmForm, AcctCostCreateForm)
from account.helpers import login_messages
from account.models import AcctCost, AcctStmt, AcctTrans, Pricing
from account.serializers import PricingSerializer
from main.mixins import RegistrationContextMixin
from main.models import UserProfile, Subaccount
from main.forms import UserCreateForm
from payment.mixins import AdminOnlyMixin, HotelUserMixin, HotelAdminCheckMixin
from sms.models import PhoneNumber
from utils import email


# from main.tasks import hello_world

### ACCOUNT ERROR / REDIRCT ROUTING VIEWS ###

@login_required(login_url=reverse_lazy('login'))
def private(request):
    messages.info(request, login_messages['now_logged_in'])
    return HttpResponseRedirect(reverse('account'))


def login_error(request):
    messages.warning(request, login_messages['login_error'])
    return HttpResponseRedirect(reverse('login'))


@login_required(login_url=reverse_lazy('login'))
def logout(request):
    auth.logout(request)
    messages.warning(request, 'You are now logged out')
    return HttpResponseRedirect(reverse('login'))


@login_required(login_url=reverse_lazy('login'))
def verify_logout(request):
    return render(request, 'cpanel/form-success/verify_logout.html')


### ACCOUNT VIEWS ###

class AccountView(LoginRequiredMixin, HotelUserMixin, TemplateView):
    """
    Main Account (profile) View.

    First time this is dispatched, make sure:
    - Hotel has a subaccount_sid
    - Assign a Twilio Ph #
    """
    template_name = 'cpanel/account.html'

    def get_context_data(self, **kwargs):
        '''TODO: clean up logic here b/4 produciton
            move `get_or_create` to a helper method?

            If move PhoneNumber.get_or_create + Subaccount.get_or_create
                to a Celery Job, can use:
                    `select_related() so only 1 query instead of 2?
        '''
        context = super(AccountView, self).get_context_data(**kwargs)

        # TODO: 
        # Move PH/Subaccount Creation to Celery n not in View request loop!
        
        # Make sure the Hotel has a Phone Number
        # phone_number, created = PhoneNumber.objects.get_or_create(
        #     hotel=self.hotel)
        # context['phone_number'] = phone_number

        # subaccount, created = Subaccount.objects.get_or_create(
        #     hotel=self.hotel)
        # context['subaccount'] = subaccount

        context['hotel'] = self.hotel

        return context


### REGISTRATION VIEWS ###

class PickPlanView(LoginRequiredMixin, RegistrationContextMixin, CreateView):
    """
    Step #3 of Registration

    Pick a Plan, and save the Plan as a `session cookie` before creating
    the Stipe Customer/Subscription using the Plan Choice.
    """
    model = AcctCost
    form_class = AcctCostCreateForm
    template_name = 'frontend/register/register.html'
    success_url = reverse_lazy('payment:register_step4')

    def get_context_data(self, **kwargs):
        context = super(PickPlanView, self).get_context_data(**kwargs)
        context['step_number'] = 2
        context['step'] = context['steps'][context['step_number']]
        return context

    def form_valid(self, form):
        '''Add the Hotel Obj to the AcctCost instance b/4 saving.'''
        self.object = form.save(commit=False)
        self.object.hotel = self.request.user.profile.hotel
        self.object.save()
        return super(PickPlanView, self).form_valid(form)


#############
# ACCT STMT #
#############

class AcctStmtListView(AdminOnlyMixin, SetHeadlineMixin, ListView):
    '''AcctStmt by Month.'''

    headline = _("Account Statements")
    template_name = 'list.html'

    def get_queryset(self):
        return AcctStmt.objects.filter(hotel=self.hotel)

    def get(self, request, *args, **kwargs):
        '''Ensure the current month's AcctStmt is up to date.

        TODO: Make this a daiy job, and not in the View.get()
        '''
        # acct_stmt = update_current_acct_stmt(hotel=self.hotel)
        return super(AcctStmtListView, self).get(request, *args, **kwargs)


class AcctStmtDetailView(AdminOnlyMixin, TemplateView):
    '''
    All AcctTrans for a single Month.

    Organized in 4 blocks, by:
        Initial Monthly Balance
        Credits - detail
                - total
        Debits  - detail
                - total
        Balance - total
    '''
    template_name = 'account/acct_trans_detail.html'

    def get_context_data(self, **kwargs):
        '''
        TODO
        ----
        Move get custom `context` logic to a helper method to clean up view.
        '''
        context = super(AcctStmtDetailView, self).get_context_data(**kwargs)

        # Use All Time Hotel Transactions to get the Balance
        all_trans = AcctTrans.objects.filter(hotel=self.hotel)

        # New Context
        context['init_balance'] = (all_trans.previous_monthly_trans(hotel=self.hotel,
                                                                    month=kwargs['month'],
                                                                    year=kwargs['year'])
                                            .balance())
        monthly_trans = (all_trans.monthly_trans(hotel=self.hotel,
                                                 month=kwargs['month'],
                                                 year=kwargs['year'])
                                  .order_by('created'))
        context['monthly_trans'] = monthly_trans
        context['balance'] = all_trans.balance()

        return context


##############
# CLOSE ACCT #
##############

class CloseAcctView(AdminOnlyMixin, SetHeadlineMixin, FormView):
    '''
    Steps
    -----
    Release Twilio Ph(s)
    Suspend Twilio Subaccount
    Refund and Account Credits via Stripe Refund
    Deactivate Hotel
    Deactivate Users
    Delete Stripe Cards

    Notes
    -----
    Will be done via Celery daily per Hotel request. So as not to slow down
        request/response cycle of normal web activity.
    Email CloseAcct confirmation to AdminUser w/ refund details, etc...

    '''
    headline = _("Close Account")
    form_class = CloseAccountForm
    template_name = 'account/account_form.html'

    def get_success_url(self):
        return reverse('close_acct_confirm',
            kwargs={'slug': self.hotel.customer.short_pk})


class CloseAcctConfirmView(AdminOnlyMixin, SetHeadlineMixin, FormView):
    '''
    Expl
    ----
    Cannot be reversed, ph #(s) released
    If you want to use the services in the future, please go through
        the normal signup process.
    Will recieve email with confirmation of "close acct" request
    Takes 24 hours to process request
    Payment refund take 5-7 business days
    Any questions, please contact: billing@textress.com
    PH # for questions, 775-419-4000
    '''

    headline = _("Confirm Close Account")
    form_class = CloseAcctConfirmForm
    template_name = 'account/account_form.html'
    success_url = reverse_lazy('close_acct_success')

    def form_valid(self, form):
        '''
        TODO: dispatch request to Celery
            - Send email that "request has been submitted"
        '''
        msg = email.close_account_email(self.request.user)
        msg.send()
        return super(CloseAcctConfirmView, self).form_valid(form)


class CloseAcctSuccessView(AdminOnlyMixin, SetHeadlineMixin, TemplateView):
    '''
    TODO
    ----
    `context`: 
        submitted, takes: 
            Takes 24 hours to process request
            Payment refund take 5-7 business days
        msg:
            "thank you and we hope that we can do Biz again in future."

    '''
    headline = _("Close Account Request Submitted")
    template_name = 'template.html'

    def get_context_data(self, **kwargs):
        context = super(CloseAcctSuccessView, self).get_context_data(**kwargs)
        context['message'] = "Thank you and we hope that we can do Biz again in future."
        return context


### REINSTATE ACCT: Not in use ###

class ReinstateAcctView(View):
    '''
    Steps
    -----
    AdminUser reactivates his User
    Reactivate Hotel
    Confirm Pmt details. ex- $10 refills at $0 balance
    Make Pmt
    Activate Twilio Subaccount
    AdminUser chooses new Twilio Ph #
    Activate Users

    Notes
    -----
    Will use similar steps to "Signup Process"

    '''
    pass


########
# REST #
########

class PricingListAPIView(generics.ListAPIView):
    '''No permissions needed b/c read only list view, and will be used 
    on the Biz Site.'''

    queryset = Pricing.objects.all()
    serializer_class = PricingSerializer

    def list(self, request, *args, **kwargs):
        '''For JSON Encoding.'''

        serializer = PricingSerializer(self.queryset, many=True)
        return Response(serializer.data)


class PricingRetrieveAPIView(generics.RetrieveAPIView):

    queryset = Pricing.objects.all()
    serializer_class = PricingSerializer