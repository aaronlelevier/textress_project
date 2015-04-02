from django import forms
from django.contrib import messages

from contact.models import Newsletter


class NewsletterForm(forms.ModelForm):
    '''
    Will eventually show as the footer on most pages.

    For now, it is on the "coming soon" page. All early signups
    will get smthn extra, which we can tell by the date created.
    '''
    class Meta:
        model = Newsletter
        fields = ('email',)