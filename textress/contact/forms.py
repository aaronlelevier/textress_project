from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError

from contact.models import Newsletter


class NewsletterForm(forms.ModelForm):
    '''
    Will eventually show as the footer on most pages.

    For now, it is on the "coming soon" page. All early signups
    will get smthn extra, which we can tell by the date created.
    '''
    error_messages = {
        'already': "You have already signed up for our pre-launch! Thank you."
    }

    class Meta:
        model = Newsletter
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Newsletter.objects.filter(email=email).exists():
            raise ValidationError(self.error_messages['already'])
        return email