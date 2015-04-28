import re
import twilio

from django.conf import settings
from django.shortcuts import render
from django.views.generic import FormView, CreateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, Http404, HttpResponseRedirect

from braces.views import LoginRequiredMixin, PermissionRequiredMixin

from .models import Text, DemoCounter, PhoneNumber
from .forms import (DemoForm, PhoneNumberForm, PhoneNumberSelectForm,
    PhoneNumberAddForm)
from .helpers import send_text, sms_messages, get_weather
from payment.views import HotelAdminCheckMixin
from utils.exceptions import DailyLimit
from utils.hotel import TwilioHotel


class DemoView(FormView):
    """
    Let's User try out Twilio SMS sending.
    Max SMS send limit == settings.SMS_LIMIT
    """
    template_name = 'sms/demo.html'
    form_class = DemoForm
    success_url = reverse_lazy('sms:demo')

    def form_valid(self, form):
        cd = form.cleaned_data
        text = Text.objects.create(**cd)
        if text:
            try:
                sent = send_text(text)
                msg = sms_messages['sent']
            except twilio.TwilioRestException:
                msg = sms_messages['send_failed']
            messages.info(self.request, msg)
        return super().form_valid(form)


# class PhoneNumberListView(LoginRequiredMixin,
#                           HotelAdminCheckMixin,
#                           FormView):
#     """Lists all PhoneNumber Obj available for the Hotel with a Form
#     to change the `is_primary` PhoneNumber."""
#     template_name = 'sms/phone_number_list.html'
#     form_class = PhoneNumberForm
#     success_url = reverse_lazy('sms:phone_number_list')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['phone_numbers'] = self.hotel.phonenumber_set.all()
#         return context

#     def get_form_kwargs(self):
#         """Attaches the Hotel's PhoneNumbers to the Form, so that each
#         PhoneNumber is available to set as "Primary" Ph # for the Hotel."""
#         kwargs = super().get_form_kwargs()
#         kwargs['phone_numbers'] = self.hotel.phonenumber_set.all()
#         return kwargs

#     def form_valid(self, form):
#         print(form.cleaned_data)
#         return super().form_valid(form)


# class PhoneNumberSelectView(LoginRequiredMixin,
#                             HotelAdminCheckMixin,
#                             FormView):
#     """Adds a Twilio PhoneNumber Obj. as a cookie, and sends the User
#     to a `Confirm Purchase View`."""
#     template_name = 'radio_form.html'
#     form_class = PhoneNumberSelectForm
#     success_url = reverse_lazy('sms:phone_number_add')

#     def get_form_kwargs(self):
#         """Needed kwargs to get available phone numbers based on Hotel
#         and save it to request.session['cookie']."""
#         kwargs = super().get_form_kwargs()
#         kwargs['request'] = self.request
#         kwargs['twilio_hotel'] = TwilioHotel(hotel=self.hotel)
#         return kwargs

#     def form_valid(self, form):
#         print(form.cleaned_data)
#         return super().form_valid(form)


# class PhoneNumberAddView(LoginRequiredMixin,
#                          HotelAdminCheckMixin,
#                          FormView):
#     template_name = 'basic_form.html'
#     form_class = PhoneNumberAddForm
#     success_url = reverse_lazy('sms:phone_number_list')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['question'] = "Purchase {} for $1".format(self.request.session['phone_number'])
#         context['submit_button'] = "Confirm"
#         return context

#     def form_valid(self, form):
#         "Purchase Twilio Ph # Obj here, and add to related models."
#         phone_number = PhoneNumber.objects.twilio_create(
#             phone_number=self.request.session['phone_number'], hotel=self.hotel)
#         return super().form_valid(form)





