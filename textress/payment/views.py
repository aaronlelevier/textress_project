from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView, FormView
from django.contrib.auth.decorators import login_required

import stripe
from braces.views import SetHeadlineMixin, FormValidMessageMixin, LoginRequiredMixin

from account.mixins import AcctCostContextMixin
from account.models import AcctCost, AcctStmt, AcctTrans
from account.tasks import create_initial_acct_trans_and_stmt
from concierge.tasks import create_hotel_default_help_reply, create_hotel_default_send_welcome
from main.mixins import (RegistrationContextMixin, HotelContextMixin, HotelUserMixin,
    AdminOnlyMixin)
from payment.models import Card
from payment.forms import StripeForm, CardListForm, OneTimePaymentForm
from payment.helpers import signup_register_step4
from payment.mixins import (StripeMixin, StripeFormValidMixin, HotelCardOnlyMixin,
    BillingSummaryContextMixin, MonthYearContextMixin)
from sms.models import PhoneNumber
from utils.email import Email
from utils import dj_messages


### REGISTRATION

class RegisterPmtView(LoginRequiredMixin, AdminOnlyMixin, RegistrationContextMixin,
    MonthYearContextMixin, AcctCostContextMixin, StripeMixin, FormView):
    """
    Step #4 of Registration

    - Dispaly Summary of Info
    - Process Payment
    - Send Email Confirmation.
    """

    template_name = 'frontend/register/payment.html'
    form_class = StripeForm
    success_url = reverse_lazy('payment:register_success')

    def get_context_data(self, **kwargs):
        context = super(RegisterPmtView, self).get_context_data(**kwargs)
        context['step_number'] = 3
        context['step'] = context['steps'][context['step_number']]
        context['PHONE_NUMBER_CHARGE'] = settings.PHONE_NUMBER_CHARGE
        return context

    def form_valid(self, form):
        try:
            (customer, card, charge) = signup_register_step4(
                hotel=self.request.user.profile.hotel,
                token=form.cleaned_data['stripe_token'],
                email=self.request.user.email,
                amount=self.hotel.acct_cost.init_amt)
        except stripe.error.StripeError as e:
            body = e.json_body
            err = body['error']
            messages.warning(self.request, err)
            return HttpResponseRedirect(reverse('payment:register_step4'))
        else:
            email = Email(
                to=self.request.user.email,
                from_email=settings.DEFAULT_EMAIL_BILLING,
                extra_context={
                    'user': self.request.user,
                    'customer': customer,
                    'charge': charge
                },
                subject='email/payment_subject.txt',
                html_content='email/payment_email.html'
            )
            email.msg.send()

            create_initial_acct_trans_and_stmt.delay(self.hotel.id)
            create_hotel_default_help_reply.delay(self.hotel.id)
            create_hotel_default_send_welcome.delay(self.hotel.id)

            return HttpResponseRedirect(self.success_url)


class RegisterSuccessView(LoginRequiredMixin, AdminOnlyMixin, RegistrationContextMixin, TemplateView):
    """
    Step #5 of Registration - Payment Success

    Confirmation Details: User, Hotel, Customer(Stripe)

    If the User hasn't completed all steps, redirect to Step4 to display needed 
    steps b/4 they can complete Payment.
    """
    template_name = 'frontend/register/success.html'

    def get(self, request, *args, **kwargs):
        # Only allow if Payment is complete
        if self.hotel.registration_complete:
            return super(RegisterSuccessView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('payment:register_step4'))

    def get_context_data(self, **kwargs):
        context = super(RegisterSuccessView, self).get_context_data(**kwargs)
        context['step_number'] = 4
        context['step'] = context['steps'][context['step_number']]
        return context


### BILLING

class SummaryView(LoginRequiredMixin, AdminOnlyMixin, SetHeadlineMixin, TemplateView):
    '''
    Main Billing Summary View with links to view more detail of 
    payment transactions, and manage account payment settings.
    '''

    headline = "Billing Overview"
    template_name = 'payment/summary.html'

    def get(self, request, *args, **kwargs):
        """
        If no AcctStmt's exist for the Hotel, bypyass this section.
        """
        context = self.get_context_data(**kwargs)

        queryset = AcctStmt.objects.filter(hotel=self.hotel)
        if queryset:
            try:
                date = request.GET.get('date')
                year, month = date.split('-')
                acct_stmt = queryset.get(year=year, month=month)  
            except (KeyError, AttributeError):
                acct_stmt = queryset.first()
            finally:
                context.update({
                    'year': acct_stmt.year,
                    'month': acct_stmt.month,
                    'acct_stmt': acct_stmt
                })
        else:
            context['acct_stmt'] = None

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(SummaryView, self).get_context_data(**kwargs)
        # new
        context['acct_stmt_starting_balance'] = AcctStmt.objects.starting_balance(hotel=self.hotel)
        # legacy
        context['acct_stmts'] = AcctStmt.objects.filter(hotel=self.hotel)
        context['acct_cost'], created = AcctCost.objects.get_or_create(hotel=self.hotel)
        context['acct_trans'] = AcctTrans.objects.filter(hotel=self.hotel,
            trans_type__name__in=['init_amt', 'recharge_amt']).order_by('-insert_date')[:4]
        return context


### CARD VIEWS ###

class CardListView(LoginRequiredMixin, AdminOnlyMixin, BillingSummaryContextMixin, MonthYearContextMixin,
    SetHeadlineMixin, FormValidMessageMixin, StripeMixin, FormView):
    '''
    Admin Only. Add a Card to an existing Customer Account View.
    '''
    headline = "Manage Payment Methods"
    template_name = "payment/card_list.html"
    form_class = CardListForm
    success_url = reverse_lazy('payment:card_list')

    def get_form_kwargs(self):
        kwargs = super(CardListView, self).get_form_kwargs()
        kwargs['hotel'] = self.hotel
        return kwargs

    def get_form_valid_message(self):
        return "The payment has been successfully processed. An email will be"
               "sent to {}. Thank you.".format(self.request.user.email)

    def form_valid(self, form):
        try:
            #DB create
            Card.objects.stripe_create(
                customer=self.request.user.profile.hotel.customer,
                token=form.cleaned_data['stripe_token']
                )
        except stripe.error.StripeError as e:
            body = e.json_body
            err = body['error']
            messages.warning(self.request, err)
            return HttpResponseRedirect(reverse('payment:one_time_payment'))
        else:
            return HttpResponseRedirect(self.success_url)


@login_required(login_url=reverse_lazy('login'))
def set_default_card_view(request, pk):
    card = Card.objects.update_default(request.user.profile.hotel.customer, pk)
    messages.success(request, '{0} ending in: {1} set as primary'.format(
        card.brand, card.last4))
    return HttpResponseRedirect(reverse('payment:card_list'))


@login_required(login_url=reverse_lazy('login'))
def delete_card_view(request, pk):
    card = Card.objects.get(pk=pk)
    Card.objects.delete_card(request.user.profile.hotel.customer, pk)
    messages.success(request, '{0} ending in: {1} deleted'.format(
        card.brand, card.last4))
    return HttpResponseRedirect(reverse('payment:card_list'))


class OneTimePaymentView(LoginRequiredMixin, AdminOnlyMixin, MonthYearContextMixin,
    SetHeadlineMixin, StripeMixin, FormView):

    headline = "One Time Payment"
    template_name = "payment/one_time_payment.html"
    form_class = OneTimePaymentForm
    success_url = reverse_lazy('payment:summary')

    def get_form_kwargs(self):
        "The Hotel Card objects will be need for the C.Card ChoiceField."
        # grab the current set of form #kwargs
        kwargs = super(OneTimePaymentView, self).get_form_kwargs()
        # Update the kwargs with the user_id
        kwargs['hotel'] = self.hotel
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(OneTimePaymentView, self).get_context_data(**kwargs)
        context['card'] = Card.objects.default(customer=self.hotel.customer)
        return context

    def form_valid(self, form):
        # super to get final form data befor processing
        super(OneTimePaymentView, self).form_valid(form)
        cd = form.cleaned_data

        try:
            # amount = int(cd['amount']) # form data 'amount' is a string
            AcctTrans.objects.one_time_payment(self.hotel, cd['amount'])
        except stripe.error.StripeError as e:
            messages.warning(self.request, dj_messages['payment_fail'].format(
                support_email=settings.DEFAULT_EMAIL_SUPPORT))
            return HttpResponseRedirect(reverse('payment:one_time_payment'))
        else:
            messages.success(self.request, dj_messages['payment_success'].format(
                amount=cd['amount']/100.0, email=self.hotel.admin.email))
            return HttpResponseRedirect(self.success_url)
