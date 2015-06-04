import re
import twilio

from django.conf import settings
from django.shortcuts import render
from django.views.generic import FormView, CreateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, Http404, HttpResponseRedirect

from braces.views import (LoginRequiredMixin, PermissionRequiredMixin,
    GroupRequiredMixin, SetHeadlineMixin)

from sms.models import PhoneNumber
from sms.forms import (PhoneNumberForm, PhoneNumberSelectForm,
    PhoneNumberAddForm)
from payment.mixins import HotelAdminCheckMixin
from utils.exceptions import DailyLimit
from utils.hotel import TwilioHotel


class PhoneNumberBaseView(GroupRequiredMixin, SetHeadlineMixin, HotelAdminCheckMixin, FormView):
    '''All phone number views require the same permissions, and context mixins. 
    Just the attrs are different.'''
    pass


class PhoneNumberListView(PhoneNumberBaseView):
    """
    Lists all PhoneNumber Obj available for the Hotel with a Form
    to change the `is_primary` PhoneNumber.
    """
    group_required = ["hotel_admin"]
    headline = "Phone Number List"
    template_name = 'sms/ph_num_list.html'
    form_class = PhoneNumberForm
    success_url = reverse_lazy('sms:ph_num_list')

    def get_context_data(self, **kwargs):
        context = super(PhoneNumberListView, self).get_context_data(**kwargs)
        context['phone_numbers'] = self.hotel.phonenumbers.all()
        return context

    def get_form_kwargs(self):
        """
        Attaches the Hotel's PhoneNumbers to the Form, so that each
        PhoneNumber is available to set as "Primary" Ph # for the Hotel.
        """
        kwargs = super(PhoneNumberListView, self).get_form_kwargs()
        kwargs['phone_numbers'] = self.hotel.phonenumbers.all()
        return kwargs

    def form_valid(self, form):
        print(form.cleaned_data)
        return super(PhoneNumberListView, self).form_valid(form)


class PhoneNumberSelectView(PhoneNumberBaseView):
    """
    Adds a Twilio PhoneNumber Obj. as a cookie, and sends the User
    to a `Confirm Purchase View`.
    """
    group_required = ["hotel_admin"]
    headline = "Select a Phone Number"
    template_name = 'cpanel/form_ph_num_buy.html'
    form_class = PhoneNumberSelectForm
    success_url = reverse_lazy('sms:ph_num_add')

    def get_form_kwargs(self):
        """Needed kwargs to get available phone numbers based on Hotel
        and save it to request.session['cookie']."""
        kwargs = super(PhoneNumberSelectView, self).get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['twilio_hotel'] = TwilioHotel(hotel=self.hotel)
        return kwargs

    def form_valid(self, form):
        # TODO: remove in prod, only printing for testing
        print(form.cleaned_data)
        return super(PhoneNumberSelectView, self).form_valid(form)


class PhoneNumberAddView(PhoneNumberBaseView):
    '''
    Form with no input, just confirms purchasing the ph num.
    '''
    group_required = ["hotel_admin"]
    headline = "Confirm to Purchase a Phone Number"
    template_name = 'cpanel/form_ph_num_buy.html'
    form_class = PhoneNumberAddForm
    success_url = reverse_lazy('sms:ph_num_add')

    def get_context_data(self, **kwargs):
        context = super(PhoneNumberAddView, self).get_context_data(**kwargs)
        context['question'] = "Purchase {} for ${}".format(
            self.request.session['phone_number'], settings.PHONE_NUMBER_CHARGE/100)
        context['submit_button'] = "Confirm"
        return context

    def form_valid(self, form):
        "Purchase Twilio Ph # Obj here, and add to related models."
        phone_number = PhoneNumber.objects.twilio_create(
            phone_number=self.request.session['phone_number'], hotel=self.hotel)
        return super(PhoneNumberAddView, self).form_valid(form)