from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from djangular.forms.fields import FloatField

from djangular.forms import NgFormValidationMixin
from djangular.styling.bootstrap3.forms import (Bootstrap3Form,
    Bootstrap3ModelForm)

from contact.models import Contact, Newsletter


class ContactForm(Bootstrap3ModelForm):

    class Meta:
        model = Contact  
        fields = ('name', 'email', 'subject', 'message',)
        widgets = {
            'message': forms.Textarea(attrs={'cols': 40, 'rows': 6.5}),
        }


class NewsletterFormAngular(NgFormValidationMixin, Bootstrap3Form):
    '''
    Footer Newsletter Form
    ----------------------
    For when site main Biz Homepage is redone to be in the Footer.

    TODO
    ----
    Switch the "Landing Page" form out for this one when ready.
    '''
    form_name = 'newsletter_form'

    email = forms.EmailField(label='E-Mail', required=True,
        help_text='Please enter a valid email address')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        obj, created = Newsletter.objects.get_or_create(email=email)
        return obj.email


class NewsletterForm(forms.ModelForm):
    '''
    Landing Page Form
    -----------------
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