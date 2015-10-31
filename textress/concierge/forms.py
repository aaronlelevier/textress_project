import datetime

from django import forms
from django.utils import timezone

from djangular.forms import NgFormValidationMixin

from concierge.models import Guest
from utils import ph_formatter, validate_phone
from utils.forms import Bootstrap3ModelForm


class GuestForm(NgFormValidationMixin, Bootstrap3ModelForm):

    form_name = 'guest_form'

    error_messages = {
        'number_in_use': "Guest phone number exists."
    }

    phone_number = forms.RegexField(r'^(\(\d{3}\)) (\d{3})-(\d{4})$',
        label='Phone number',
        error_messages={'invalid': 'Phone number have 10 digits'},
        help_text='Allowed phone number format: (702) 510-5555')
    check_in = forms.DateField(label='Check-in Date',
        initial=timezone.now(),
        # not allowing 1st of month, and raising a form error instead, so for the time being,
        # just use jqery.maskedinput
        # widget=forms.DateInput(attrs={'validate-date': r'^(\d{4})-(\d{1,2})-(\d{1,2})$'}),
        help_text='Allowed date format: yyyy-mm-dd')
    check_out = forms.DateField(label='Check-out Date',
        initial=timezone.now()+datetime.timedelta(days=1),
        # widget=forms.DateInput(attrs={'validate-date': r'^(\d{4})-(\d{1,2})-(\d{1,2})$'}),
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
