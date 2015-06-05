from django import forms
from django.conf import settings

from sms.models import PhoneNumber


class PhoneNumberForm(forms.Form):

    def __init__(self, hotel, phone_numbers, *args, **kwargs):
        super(PhoneNumberForm, self).__init__(*args, **kwargs)

        # attach PhoneNumbers to Form
        self.hotel = hotel
        self.phone_numbers = phone_numbers
        self.ph_num_primary = self.phone_numbers.primary(self.hotel)
        self.ph_num_choices = [(ph.sid, ph.friendly_name) for ph in self.phone_numbers]
        # Fields
        self.fields['phone_numbers'] = forms.ChoiceField(widget=forms.RadioSelect,
            choices=self.ph_num_choices, initial=self.ph_num_initial)

    @property
    def ph_num_initial(self):
        '''Inital Primary Phone number for the form.

        Note: Needs to return the "Value" from the (Value,human-readable) in
        order to populate the form.
        '''
        if self.ph_num_primary:
            return self.ph_num_primary.sid

    def clean(self):
        cd = super(PhoneNumberForm, self).clean()
        ph_num = PhoneNumber.objects.update_primary(hotel=self.hotel,
            sid=cd['phone_numbers'])
        return cd


class PhoneNumberAddForm(forms.Form):
    "No fields. Just accept a POST action, and create PhoneNumber Obj."
    pass