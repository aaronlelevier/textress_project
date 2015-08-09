import datetime

from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth, messages

import stripe
from braces.views import LoginRequiredMixin, GroupRequiredMixin

from payment.models import Card
from payment.helpers import signup_register_step4
from main.models import Hotel
from utils import dj_messages, mixins
from utils.email import Email


### MISC.

class BillingSummaryContextMixin(mixins.BreadcrumbBaseMixin):

    def __init__(self):
        self.clip_icon = 'clip-banknote'
        self.url = reverse('payment:summary')
        self.url_name = 'Billing Overview'


class MonthYearContextMixin(object):
    "For Form Month/Year dropdown ChoiceFields."

    def get_context_data(self, **kwargs):
        context = super(MonthYearContextMixin, self).get_context_data(**kwargs)
        context['months'] = ['<option value="{num:02d}">{num:02d}</option>'.format(num=i) for i in range(1,13)]
        cur_year = datetime.date.today().year
        context['years'] = ['<option value="{num}">{num}</option>'.format(num=i) for i in range(cur_year, cur_year+12)]
        return context


### STRIPE

class StripeMixin(object):
    
    def get_context_data(self, **kwargs):
        context = super(StripeMixin, self).get_context_data(**kwargs)
        context['publishable_key'] = settings.STRIPE_PUBLIC_KEY
        return context


class StripeFormValidMixin(object):
    '''
    Logic for different Views that need to process Payments 
    using a Stripe Form.
    '''

    def form_valid(self, form):
        try:
            #DB create
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
            # send conf email
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
            return HttpResponseRedirect(self.success_url)


### CARD

class HotelCardOnlyMixin(object):
    '''Make sure that the Card belongs to the Hotel.'''

    def dispatch(self, request, *args, **kwargs):
        self.hotel = self.request.user.profile.hotel

        self.short_pk = kwargs['pk']

        if self.short_pk not in (
            Card.objects.filter(customer=self.hotel.customer)
                        .values_list('short_pk', flat=True)):
            raise Http404

        return super(HotelCardOnlyMixin, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        try:
            return Card.objects.get(short_pk=self.short_pk)
        except ObjectDoesNotExist:
            raise Http404