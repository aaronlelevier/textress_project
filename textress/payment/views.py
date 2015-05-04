import stripe

from django import forms
from django.conf import settings
from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse, reverse_lazy
from django.template import RequestContext
from django.utils.html import escape
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (ListView, DetailView, CreateView, DeleteView,
    FormView, UpdateView)
from django.views.generic.base import View, TemplateView
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist

from braces.views import (LoginRequiredMixin, PermissionRequiredMixin,
    GroupRequiredMixin)

from payment.models import Customer, Card, Charge
from payment.forms import StripeForm
from payment.helpers import signup_register_step4
from payment.mixins import (StripeMixin, HotelContextMixin, HotelUserMixin,
    HotelAdminCheckMixin, AdminOnlyMixin, HotelCardOnlyMixin, AcctCostContextMixin)
from account.models import AcctCost
from main.models import Hotel
from main.mixins import RegistrationContextMixin
from sms.models import PhoneNumber


### REGISTRATION VIEWS ###

class RegisterPmtView(RegistrationContextMixin, AdminOnlyMixin,
    AcctCostContextMixin, StripeMixin, TemplateView):
    """
    Step #4 of Registration

    TODO: Add terms-n-cond, disclaimer(ph's puchased are $1 each. Only 1 ph # needed,
        unless you want to change your phone #, ph # is a separate charge to account.)
    """

    template_name = 'payment/payment.html'
    form_class = StripeForm
    success_url = reverse_lazy('payment:register_success')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['step_number'] = 3
        context['step'] = context['steps'][context['step_number']]
        return context

    def post(self, request, *args, **kwargs):
        try:
            print('token', request.POST['stripeToken'])
            #DB create
            (customer, card, charge) = signup_register_step4(
                hotel=self.hotel,
                token=request.POST['stripeToken'],
                email=request.POST['stripeEmail'],
                amount=self.hotel.acct_cost.init_amt)
        except stripe.error.StripeError as e:
            body = e.json_body
            err = body['error']
            messages.warning(self.request, err)
            return HttpResponseRedirect(reverse('payment:register_step4'))
        else:
            return HttpResponseRedirect(self.success_url)


class RegisterSuccessView(AdminOnlyMixin, TemplateView):
    """
    Step #5 of Registration - Success

    Confirmation Details: User account, Hotel, Stripe

    TODO: 
        - create payment conf details Here
        - send a signup email confirmation

    """
    template_name = 'payment/success.html'


### CARD VIEWS ###

class CardListView(AdminOnlyMixin, ListView):
    '''All Cards for the Hotel.

    TODO: Later maybe add this as a template sub-piece to the 
        accounts:account View w/ Admin Permission Tag on the Template.
    '''
    template_name = 'list.html'

    def get_queryset(self):
        return Card.objects.filter(customer=self.hotel.customer)


class CardCreateView(AdminOnlyMixin, 
                     StripeMixin,
                     AcctCostContextMixin,
                     TemplateView):
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