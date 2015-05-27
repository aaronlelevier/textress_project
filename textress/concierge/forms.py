from django import forms
from django.conf import settings

from twilio import twiml, TwilioRestException 

from concierge.models import Message
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






















