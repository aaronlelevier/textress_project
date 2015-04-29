from django import forms
from django.forms.widgets import RadioSelect
from django.conf import settings
from django.utils.timezone import now 

from sms.models import Text, DemoCounter
from sms.helpers import sms_messages, clean_to
from utils.exceptions import DailyLimit


class DemoForm(forms.ModelForm):

    class Meta:
        model = Text 
        fields = ('to',)


    def clean(self):
        """
        First validate SMS limit for the day has not been reached.
        - create new record (or retrieve the one for the day)
        - check count: if < settings.SMS_LIMIT raise error; else continue
        """
        cleaned_data = super().clean()

        # Check SMS sent count for the day
        try:
            dc = DemoCounter.objects.create_count()
        except DailyLimit:
            raise forms.ValidationError(sms_messages['limit_reached'])

        self, cleaned_data = clean_to(obj=self, cleaned_data=cleaned_data)

        return cleaned_data


class PhoneNumberForm(forms.Form):

    def __init__(self, phone_numbers, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # attach PhoneNumbers to Form
        self.phone_numbers = phone_numbers
        self.fields['phone_number'] = forms.RadioSelect(
            choices=[(ph.sid, ph.friendly_name) for ph in self.phone_numbers])


class PhoneNumberSelectForm(forms.Form):
    "Display 10 Available Twilio PhoneNumber Obj, and add to cookie."

    # PHONES = (('1','A'), ('2', 'B'))

    # radio = forms.ChoiceField( widget=RadioSelect(), choices=PHONES)


    def __init__(self, request, twilio_hotel, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # attach Available PhoneNumbers to Form
        self.request = request
        self.phone_numbers = twilio_hotel.available_phone_numbers()
        self.fields['phone_number'] = forms.ChoiceField(widget=RadioSelect(),
            choices=[(ph.phone_number, ph.friendly_name) for ph in self.phone_numbers])

        def clean(self):
            cleaned_data = super.clean()

            phone_number = cleaned_data.get("phone_number")
            self.request.session['phone_number'] = phone_number
            print('form cookie', request.session['phone_number'])
            return cleaned_data
            

class PhoneNumberAddForm(forms.Form):
    "No fields. Just accept a POST action, and create PhoneNumber Obj."
    pass


















