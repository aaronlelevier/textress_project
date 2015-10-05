import sys

from django.conf import settings
from django.template.loader import render_to_string
from django.views.generic import FormView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from braces.views import (SetHeadlineMixin, FormValidMessageMixin,
    FormInvalidMessageMixin)

from main.mixins import AdminOnlyMixin
from sms.forms import PhoneNumberAddForm
from sms.models import PhoneNumber
from utils.exceptions import PhoneNumberNotDeletedExcp
from utils.forms import EmptyForm


class PhoneNumberBaseView(AdminOnlyMixin, SetHeadlineMixin, FormValidMessageMixin, FormView):
    '''All phone number views require the same permissions, and context mixins. 
    Just the attrs are different.'''
    pass


class PhoneNumberListView(PhoneNumberBaseView):
    """
    Lists all PhoneNumber Obj available for the Hotel with a Form
    to change the `is_primary` PhoneNumber.
    """
    headline = "Phone Number List"
    template_name = 'sms/ph_num_list.html'
    form_class = EmptyForm
    success_url = reverse_lazy('sms:ph_num_list')
    form_valid_message = "Primary Phone Number successfully updated"

    def get_context_data(self, **kwargs):
        context = super(PhoneNumberListView, self).get_context_data(**kwargs)
        context['phone_numbers'] = self.hotel.phonenumbers.order_by('-default')
        context['addit_info'] = render_to_string('cpanel/forms/form_ph_list.html',
            {'ph_num_monthly_cost': settings.PHONE_NUMBER_MONTHLY_COST})
        return context


class PhoneNumberAddView(FormInvalidMessageMixin, PhoneNumberBaseView):
    '''
    Form with no input, just confirms purchasing the ph num.
    '''
    headline = "Purchase a Phone Number"
    template_name = 'cpanel/form.html'
    form_class = PhoneNumberAddForm
    success_url = reverse_lazy('sms:ph_num_list')
    form_valid_message = "Phone Number successfully purchased"
    form_invalid_message = (
        "Please refill your account balance in order to "
        "process this transation or turn Auto-recharge ON."
    )

    def get_context_data(self, **kwargs):
        context = super(PhoneNumberAddView, self).get_context_data(**kwargs)
        context['addit_info'] = render_to_string("cpanel/forms/form_ph_add.html",
            {'amount': settings.PHONE_NUMBER_CHARGE, 'hotel': self.hotel})
        context['btn_text'] = "Confirm"
        return context

    def get_form_kwargs(self):
        kwargs = super(PhoneNumberAddView, self).get_form_kwargs()
        kwargs['hotel'] = self.hotel
        return kwargs

    def form_valid(self, form):
        "Purchase Twilio Ph # Obj here, and add to related models."
        if not settings.DEBUG and 'test' not in sys.argv:
            phone_number = PhoneNumber.objects.purchase_number(hotel=self.hotel)
        return super(PhoneNumberAddView, self).form_valid(form)


@login_required(login_url=reverse_lazy('login'))
def set_default_phone_number_view(request, pk):
    ph = PhoneNumber.objects.update_default(request.user.profile.hotel, pk)
    return HttpResponseRedirect(reverse('sms:ph_num_list'))


class PhoneNumberDeleteView(PhoneNumberBaseView, DeleteView):
    '''
    Admin confirms to Delete PhoneNumber here before deleting.
    '''
    group_required = ["hotel_admin"]
    headline = "Delete Phone Number"
    template_name = 'cpanel/form.html'
    form_class = EmptyForm
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
        return u"Phone number: {0} deleted!".format(self.object.friendly_name)

    def form_valid(self, form):
        try:
            self.object.delete()
        except PhoneNumberNotDeletedExcp:
            messages.add_message(self.request, messages.INFO, "Phone number delete \
failed. Please contact support at: {}".format(settings.DEFAULT_EMAIL_SUPPORT))
        return HttpResponseRedirect(self.get_success_url())