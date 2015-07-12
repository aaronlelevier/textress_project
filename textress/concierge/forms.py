import datetime

from django import forms
from django.utils import timezone

from djangular.forms import NgFormValidationMixin
from djangular.styling.bootstrap3.forms import Bootstrap3Form, Bootstrap3ModelForm

from concierge.models import Guest
from utils import ph_formatter


class GuestForm(NgFormValidationMixin, Bootstrap3ModelForm):

    form_name = 'guest_form'

    phone_number = forms.RegexField(r'^(\d{3})-(\d{3})-(\d{4})$',
        label='Phone number',
        error_messages={'invalid': 'Phone number have 10 digits'},
        help_text='Allowed phone number format: 702-510-5555')
    check_in = forms.DateField(label='Check-in Date',
        initial=timezone.now(),
        widget=forms.DateInput(attrs={'validate-date': '^(\d{4})-(\d{1,2})-(\d{1,2})$'}),
        help_text='Allowed date format: yyyy-mm-dd')
    check_out = forms.DateField(label='Check-out Date',
        initial=timezone.now()+datetime.timedelta(days=1),
        widget=forms.DateInput(attrs={'validate-date': '^(\d{4})-(\d{1,2})-(\d{1,2})$'}),
        help_text='Allowed date format: yyyy-mm-dd')
    
    class Meta:
        model = Guest
        fields = ['name', 'room_number', 'phone_number', 'check_in', 'check_out']

    def __init__(self, guest=None, *args, **kwargs):
        super(GuestForm, self).__init__(*args, **kwargs)
        # kwargs['initial'].update('phone_number': '123')
        self.initial['phone_number'] = ph_formatter(guest.phone_number)