import datetime

from django.conf import settings
from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse, reverse_lazy
from django.template import RequestContext
from django.contrib import messages
from django.views.generic import (ListView, DetailView, DeleteView, TemplateView,
    FormView, UpdateView)
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict

import stripe
from braces.views import (LoginRequiredMixin, PermissionRequiredMixin,
    GroupRequiredMixin, SetHeadlineMixin, FormValidMessageMixin)

from account.mixins import AcctCostContextMixin
from account.models import AcctCost, AcctStmt, AcctTrans
from main.models import Hotel
from main.mixins import (RegistrationContextMixin, HotelContextMixin, HotelUserMixin,
    AdminOnlyMixin)
from payment.models import Card
from payment.forms import StripeForm
from payment.helpers import signup_register_step4
from payment.mixins import StripeMixin, StripeFormValidMixin, HotelCardOnlyMixin
from sms.models import PhoneNumber
from utils.email import Email


### REGISTRATION VIEWS ###

class RegisterPmtView(RegistrationContextMixin, AdminOnlyMixin, AcctCostContextMixin,
    StripeMixin, StripeFormValidMixin, FormView):
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
        # form choices
        context['months'] = ['<option value="{num:02d}">{num:02d}</option>'.format(num=i) for i in range(1,13)]
        cur_year = datetime.date.today().year
        context['years'] = ['<option value="{num}">{num}</option>'.format(num=i) for i in range(cur_year, cur_year+12)]
        context['PHONE_NUMBER_CHARGE'] = settings.PHONE_NUMBER_CHARGE
        return context



class RegisterSuccessView(RegistrationContextMixin, AdminOnlyMixin, TemplateView):
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


class SummaryView(AdminOnlyMixin, SetHeadlineMixin, TemplateView):
    '''
    Main Billing Summary View with links to view more detail of 
    payment transactions, and manage account payment settings.
    '''

    headline = "Billing Overview"
    template_name = 'payment/summary.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        try:
            date = request.GET.get('date')
            year, month = date.split('-')
            context['acct_stmt'] = AcctStmt.objects.get(year=year, month=month)
        except (KeyError, AttributeError):
            context['acct_stmt'] = AcctStmt.objects.first()
        finally:
            context['sms_cost'] = context['acct_stmt'].balance - context['phone_numbers_cost']
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(SummaryView, self).get_context_data(**kwargs)
        context['acct_stmts'] = AcctStmt.objects.filter(hotel=self.hotel)
        context['acct_cost'], created = AcctCost.objects.get_or_create(hotel=self.hotel)
        context['phone_numbers'] = PhoneNumber.objects.filter(hotel=self.hotel)
        context['phone_numbers_cost'] = context['phone_numbers'].count() * settings.PHONE_NUMBER_MONTHLY_COST
        context['acct_trans'] = AcctTrans.objects.filter(hotel=self.hotel,
            trans_type__name__in=['init_amt', 'recharge_amt']).order_by('-insert_date')[:4]
        return context


class OneTimePaymentView(AdminOnlyMixin, SetHeadlineMixin, FormValidMessageMixin,
    StripeMixin, StripeFormValidMixin, FormView):

    headline = "One Time Payment"
    template_name = "payment/one_time_payment.html"
    form_class = StripeForm
    success_url = reverse_lazy('payment:summary')

    def get_form_valid_message(self):
        return "The payment has been successfully processed. An email will be \
sent to {}. Thank you.".format(self.request.user.email) # TODO: Is this the correct email ??


### CARD VIEWS ###

class CardCreateView(AdminOnlyMixin, StripeMixin, AcctCostContextMixin, TemplateView):
    '''Admin Only. Add a Card to an existing Customer Account View.'''

    # TODO: prbly change template_name later?
    template_name = 'payment/payment.html' 
    form_class = StripeForm
    success_url = reverse_lazy('accounts:account')

    def post(self, request, *args, **kwargs):
        try:
            card = Card.objects.stripe_create(customer=self.hotel.customer,
                token=request.POST['stripeToken'])
        except stripe.error.CardError as e:
            body = e.json_body
            err = body['error']
            print(err)
            messages.warning(self.request, err)
            return HttpResponseRedirect(reverse('payment:card_create'))
        else:
            return HttpResponseRedirect(self.success_url)


class CardDetailView(AdminOnlyMixin, HotelCardOnlyMixin, DetailView):
    '''All Cards for the Hotel. Only viewable by the Admin.

    dispatch kwargs['pk']: \w+ regex ok b/c using card.short_pk (shortened
        version of the Stripe Card ID)
    '''
    model = Card
    template_name = 'detail_view.html'


class CardUpdateView(AdminOnlyMixin, HotelCardOnlyMixin, UpdateView):

    model = Card
    fields = ['default']
    template_name = 'account/account_form.html'

    def get_success_url(self): 
        return reverse_lazy('payment:card_detail', kwargs={'pk': self.object.short_pk})


class CardDeleteView(AdminOnlyMixin, HotelCardOnlyMixin, DeleteView):

    model = Card
    template_name = 'account/account_form.html'
    success_url = reverse_lazy('payment:card_list')