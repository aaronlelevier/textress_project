from django import forms
from django.conf import settings

from twilio import twiml, TwilioRestException 

from djangular.forms import NgFormValidationMixin
from djangular.styling.bootstrap3.forms import (Bootstrap3Form,
    Bootstrap3ModelForm)

from concierge.models import Message, Guest
from sms.helpers import sms_messages, clean_to, send_message


class MessageForm(forms.ModelForm):

    class Meta:
        model = Message 
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={'cols': 50, 'rows': 4}),
        }

    def clean(self):
        cleaned_data = super(MessageForm, self).clean()
        body = cleaned_data.get("body")

        try:
            text = send_message(to=settings.DEFAULT_TO_PH, body=body)
        except TwilioRestException:
            raise forms.ValidationError("Failed to send message.")
        else:
            # TODO: if send_message() is successful. Should get the Guest data
            #   + the Twilio send data (from the API using REST? and save() it here?)
            pass

        return cleaned_data


class GuestForm(NgFormValidationMixin, Bootstrap3ModelForm):

    form_name = 'guest_form'
    
    class Meta:
        model = Guest
        fields = ['name', 'room_number', 'phone_number', 'check_in', 'check_out']