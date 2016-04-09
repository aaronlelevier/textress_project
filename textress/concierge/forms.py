import datetime

from django import forms
from django.utils import timezone

from djangular.forms import NgFormValidationMixin

from concierge.models import Guest
from utils import ph_formatter, validate_phone
from utils.forms import Bootstrap3ModelForm
from utils.models import Dates


class GuestForm(NgFormValidationMixin, Bootstrap3ModelForm):

    form_name = 'guest_form'

    error_messages = {
        'number_in_use': "Guest phone number exists",
        'check_in_past_date': "Check-in is a past date",
        'check_out_before_check_in': "Check-out date before check-in"
    }

    phone_number = forms.RegexField(r'^(\(\d{3}\)) (\d{3})-(\d{4})$',
        label='Phone number',
        error_messages={'invalid': 'Phone number have 10 digits'},
        help_text='Allowed phone number format: (702) 510-5555')
    check_in = forms.DateField(label='Check-in Date',
        help_text='Allowed date format: yyyy-mm-dd')
    check_out = forms.DateField(label='Check-out Date',
        help_text='Allowed date format: yyyy-mm-dd')
    
    class Meta:
        model = Guest
        fields = ['name', 'room_number', 'phone_number', 'check_in', 'check_out']

    def __init__(self, guest=None, *args, **kwargs):
        super(GuestForm, self).__init__(*args, **kwargs)
        self.guest = guest

        try:
            phone = guest.phone_number
        except AttributeError:
            self.initial['phone_number'] = ""
        else:
            self.initial['phone_number'] = ph_formatter(
                getattr(guest, 'phone_number', None))

        self.initial['check_in'] = timezone.localtime(timezone.now()).date()
        self.initial['check_out'] = timezone.localtime(timezone.now()).date()+datetime.timedelta(days=1)

    def clean_phone_number(self):
        """
        Return the Twilio formatted PH #
        """
        self.cleaned_data = super(GuestForm, self).clean()

        phone_number = self.cleaned_data.get('phone_number')

        # returns a validated and formatted phone # ex: "+17025108888"
        # all phone #'s saved to the DB in this format
        phone = validate_phone(phone_number)

        self._validate_phone_in_use(phone)

        return phone

    def _validate_phone_in_use(self, phone):
        """Silently pass if the Guest is updating something, but leaving
        the PH # as is."""

        qs = Guest.objects.current().filter(phone_number=phone)

        if self.guest:
            qs = qs.exclude(id=self.guest.id)

        if qs.exists():
            raise forms.ValidationError(self.error_messages['number_in_use'])

    def clean_check_in(self):
        check_in = self.cleaned_data.get("check_in")

        if check_in < Dates()._today:
            raise forms.ValidationError(self.error_messages['check_in_past_date'])

        return check_in

    def clean_check_out(self):
        check_in = self.cleaned_data.get("check_in", Dates()._today)
        check_out = self.cleaned_data.get("check_out")

        if check_out < check_in:
            raise forms.ValidationError(self.error_messages['check_out_before_check_in']
                .format(check_in=check_in, check_out=check_out))

        return check_out
