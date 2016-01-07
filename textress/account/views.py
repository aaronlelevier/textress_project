from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import auth, messages
# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View, ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, CreateView, UpdateView, ModelFormMixin

from braces.views import (LoginRequiredMixin, GroupRequiredMixin, SetHeadlineMixin,
    StaticContextMixin)
from rest_framework import generics
from rest_framework.response import Response
from ws4redis.publisher import RedisPublisher

from account.forms import (AuthenticationForm, CloseAccountForm,
    CloseAcctConfirmForm, AcctCostForm, AcctCostUpdateForm)
from account.mixins import alert_messages
from account.models import Dates, AcctCost, AcctStmt, AcctTrans, Pricing
from account.serializers import PricingSerializer
from main.mixins import RegistrationContextMixin, AdminOnlyMixin, HotelUserMixin
from payment.helpers import no_funds_alert, no_customer_alert
from payment.mixins import BillingSummaryContextMixin
from sms.helpers import no_twilio_phone_number_alert
from utils import email, login_messages
from utils.mixins import FormUpdateMessageMixin


### ACCOUNT ERROR / REDIRCT ROUTING VIEWS ###

@login_required(login_url=reverse_lazy('login'))
def private(request):
    messages.info(request, login_messages['now_logged_in'])
    return HttpResponseRedirect(reverse('account'))


@login_required(login_url=reverse_lazy('login'))
def logout(request):
    auth.logout(request)
    messages.warning(request, login_messages['now_logged_out'])
    return HttpResponseRedirect(reverse('login'))


# # TODO: I don't think that I ever hit this URL (No tests for this URL for now...)
# def login_error(request):
#     messages.warning(request, login_messages['login_error'])
#     return HttpResponseRedirect(reverse('login'))


# # TODO: I don't think that I ever hit this URL (No tests for this URL for now...)
# @login_required(login_url=reverse_lazy('login'))
# def verify_logout(request):
#     return render(request, 'cpanel/form-success/verify_logout.html')


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():
            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            _next = request.POST.get('next')
            if _next:
                return HttpResponseRedirect(_next)
            else:
                return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
        'next': request.GET.get('next')
    }
    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app

    return TemplateResponse(request, template_name, context)


### ACCOUNT VIEWS ###

class AccountView(LoginRequiredMixin, HotelUserMixin, SetHeadlineMixin,
    StaticContextMixin, TemplateView):
    """
    Account Dashboard ~ User Home Page
    """
    headline = 'Dashboard'
    static_context = {'headline_small': 'guest list & quick links'}
    template_name = 'cpanel/account.html'

    def get(self, request, *args, **kwargs):
        """
        Instantiage RedisPublisher immediately, so no lag in not getting the 1st 
        SMS Message posted to ``/api/receive/sms_url/``, and "bug" where you have 
        to do a page-refresh before they start popping on the page.
        """
        RedisPublisher(facility='foobar', broadcast=True)
        return super(AccountView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Show alert messages for pending actions needed before the 
        Account will be fully functional.
        """
        context = super(AccountView, self).get_context_data(**kwargs)
        context['alerts'] = alert_messages(messages=self._get_alert_messages())
        return context

    def _get_alert_messages(self):
        """
        Generates 'bootstrap' Alert, Info, etc... messages if any part of 
        the Hotel's required configuration is not set, and gives the User 
        a link to navigate to, to set the needed configuration.
        """
        messages = []

        subaccount = self.hotel.get_subaccount()
        if subaccount and not subaccount.active:
            messages.append(no_funds_alert()) # 'subaccount' gets deactivated when there's
                                              # isufficient funds
        if not self.hotel.customer:
            messages.append(no_customer_alert())

        if not self.hotel.twilio_ph_sid:
            messages.append(no_twilio_phone_number_alert())

        return messages


### REGISTRATION VIEWS ###

class RegisterAcctCostBaseView(GroupRequiredMixin, RegistrationContextMixin, View):
    """
    Step #3 of Registration

    Pick a Plan, and save the Plan as a `session cookie` before creating
    the Stipe Customer/Subscription using the Plan Choice.
    """
    group_required = ["hotel_admin"]
    model = AcctCost
    form_class = AcctCostForm
    template_name = 'frontend/register/register.html'
    success_url = reverse_lazy('payment:register_step4')

    def get_context_data(self, **kwargs):
        context = super(RegisterAcctCostBaseView, self).get_context_data(**kwargs)
        context['step_number'] = 2
        context['step'] = context['steps'][context['step_number']]
        return context


class RegisterAcctCostCreateView(RegisterAcctCostBaseView, CreateView):
    '''
    If AcctCost already exists for the Hotel, re-route to the UpdateView.
    '''
    def dispatch(self, request, *args, **kwargs):
        try:
            acct_cost = self.request.user.profile.hotel.acct_cost
        except AttributeError:
            return super(RegisterAcctCostCreateView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('register_step3_update', kwargs={'pk': acct_cost.pk}))

    def form_valid(self, form):
        '''Add the Hotel Obj to the AcctCost instance b/4 saving.'''

        self.object, created = self.model.objects.get_or_create(
            hotel=self.request.user.profile.hotel, **form.cleaned_data)

        return super(ModelFormMixin, self).form_valid(form)


class RegisterAcctCostUpdateView(RegisterAcctCostBaseView, UpdateView):    
    '''
    AcctCost must belong to the Admin User's Hotel.
    '''
    def dispatch(self, request, *args, **kwargs):
        try:
            # must call this or else the "object" instance of the Model
            # will not be available
            self.object = self.get_object()
            acct_cost = self.object.hotel == self.request.user.profile.hotel
        except AttributeError:
            acct_cost = None

        if not acct_cost:
            return HttpResponseRedirect(reverse('register_step3'))

        return super(RegisterAcctCostUpdateView, self).dispatch(request, *args, **kwargs)


#############
# ACCT COST #
#############

class AcctCostUpdateView(LoginRequiredMixin, AdminOnlyMixin, BillingSummaryContextMixin,
    SetHeadlineMixin, FormUpdateMessageMixin, UpdateView):

    headline = "Payment Refill Settings"
    template_name = "cpanel/form.html"
    model = AcctCost
    form_class = AcctCostUpdateForm
    success_url = reverse_lazy('payment:summary')


#############
# ACCT STMT #
#############

class AcctStmtDetailView(LoginRequiredMixin, AdminOnlyMixin, SetHeadlineMixin,
    BillingSummaryContextMixin, TemplateView):
    '''
    All AcctTrans for a single Month.
    '''
    headline = "Account Statement Detail"
    template_name = 'account/acct_trans_detail.html'

    def get_context_data(self, **kwargs):
        context = super(AcctStmtDetailView, self).get_context_data(**kwargs)
        # Use All Time Hotel Transactions to get the Balance
        _date = Dates().first_of_month(int(kwargs['month']), int(kwargs['year']))
        all_trans = AcctTrans.objects.filter(hotel=self.hotel)
        # Table Context
        context['monthly_trans'] = AcctTrans.objects.monthly_trans(self.hotel, _date).order_by('-created')
        context['acct_stmt'] = (AcctStmt.objects.filter(hotel=self.hotel)
                                                .get(month=kwargs['month'], year=kwargs['year']))
        context['acct_stmts'] = AcctStmt.objects.filter(hotel=self.hotel)
        context['debit_trans_types'] = ['sms_used', 'phone_number']
        return context


class AcctPmtHistoryView(LoginRequiredMixin, AdminOnlyMixin, SetHeadlineMixin,
    BillingSummaryContextMixin, ListView):
    '''
    Simple table view of payments that uses pagination.
    '''
    headline = "Account Payments"
    model = AcctTrans
    template_name = "account/acct_pmt_history.html"
    paginate_by = 2 if settings.DEBUG else 10

    def get_queryset(self):
        queryset = AcctTrans.objects.filter(hotel=self.hotel,
            trans_type__name__in=['init_amt', 'recharge_amt']).order_by('-insert_date')
        return queryset


########
# REST #
########

class PricingListAPIView(generics.ListAPIView):
    '''No permissions needed b/c read only list view, and will be used 
    on the Biz Site.'''

    queryset = Pricing.objects.all()
    serializer_class = PricingSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class PricingRetrieveAPIView(generics.RetrieveAPIView):

    queryset = Pricing.objects.all()
    serializer_class = PricingSerializer


### NOT IN USE ###########################################################################

##############
# CLOSE ACCT #
##############

# NotImplemented: Manually handle closing of Accounts to start, until it becomes an issue,
# then automate this.

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
    template_name = 'cpanel/form.html'

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
        Send email that "request has been submitted"
        '''
        msg = email.close_account_email(self.request.user)
        msg.send()
        return super(CloseAcctConfirmView, self).form_valid(form)


class CloseAcctSuccessView(AdminOnlyMixin, SetHeadlineMixin, TemplateView):
    '''
    NotImplemented
    --------------
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
