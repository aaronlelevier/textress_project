import re
import twilio

from django.conf import settings
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import FormView, CreateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, Http404, HttpResponseRedirect

from braces.views import (LoginRequiredMixin, PermissionRequiredMixin,
    GroupRequiredMixin, SetHeadlineMixin, FormValidMessageMixin)

from sms.models import PhoneNumber
from sms.forms import PhoneNumberForm, PhoneNumberAddForm
from payment.mixins import HotelAdminCheckMixin
from utils.exceptions import DailyLimit
from utils.hotel import TwilioHotel


class PhoneNumberBaseView(GroupRequiredMixin, SetHeadlineMixin, FormValidMessageMixin,
    HotelAdminCheckMixin, FormView):
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
    form_valid_message = "Primary Phone Number successfully updated"

    def get_context_data(self, **kwargs):
        context = super(PhoneNumberListView, self).get_context_data(**kwargs)
        context['phone_numbers'] = self.hotel.phonenumbers.all()
        context['addit_info'] = render_to_string('cpanel/forms/form_ph_list.html',
            {'ph_num_monthly_cost': settings.PHONE_NUMBER_MONTHLY_COST})
        return context

    def get_form_kwargs(self):
        """
        Attaches the Hotel's PhoneNumbers to the Form, so that each
        PhoneNumber is available to set as "Primary" Ph # for the Hotel.
        """
        kwargs = super(PhoneNumberListView, self).get_form_kwargs()
        kwargs['hotel'] = self.hotel
        kwargs['phone_numbers'] = self.hotel.phonenumbers.all()
        return kwargs


class PhoneNumberAddView(PhoneNumberBaseView):
    '''
    Form with no input, just confirms purchasing the ph num.
    '''
    group_required = ["hotel_admin"]
    headline = "Purchase a Phone Number"
    template_name = 'cpanel/form.html'
    form_class = PhoneNumberAddForm
    success_url = reverse_lazy('sms:ph_num_list')
    form_valid_message = "Phone Number successfully purchased"

    def get_context_data(self, **kwargs):
        context = super(PhoneNumberAddView, self).get_context_data(**kwargs)
        # context['question'] = "Purchase {} for ${}".format(
        #     self.request.session['phone_number'], settings.PHONE_NUMBER_CHARGE/100)
        context['addit_info'] = render_to_string("cpanel/forms/form_ph_add.html",
            {'amount': settings.PHONE_NUMBER_CHARGE, 'hotel': self.hotel})
        context['btn_text'] = "Confirm"
        return context

    def form_valid(self, form):
        "Purchase Twilio Ph # Obj here, and add to related models."
        phone_number, created = PhoneNumber.objects.get_or_create(hotel=self.hotel)
        return super(PhoneNumberAddView, self).form_valid(form)


class PhoneNumberDeleteView(PhoneNumberBaseView, DeleteView):
    '''
    Admin confirms to Delete PhoneNumber here before deleting.
    '''
    group_required = ["hotel_admin"]
    headline = "Delete Phone Number"
    template_name = 'cpanel/form.html'
    form_class = PhoneNumberAddForm # empty form here w/ no fields, just confirming delete
    success_url = reverse_lazy('sms:ph_num_list')
    model = PhoneNumber
    pk_url_kwarg = 'sid'

    def get_context_data(self, **kwargs):
        # custom context to display Delete wanted by user
        context = super(PhoneNumberDeleteView, self).get_context_data(**kwargs)
        context['addit_info'] = render_to_string('cpanel/forms/form_ph_delete.html',
            {'ph': self.object})
        # Submit Button Context
        context['btn_color'] = 'danger'
        context['btn_text'] = 'Delete'
        return context
    
    def get_form_valid_message(self):
        # dynamic msg success to show which ph num was deleted
        return u"{0} deleted!".format(self.object.friendly_name)