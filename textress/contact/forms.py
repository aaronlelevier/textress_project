from django import forms

from contact.models import Contact
from utils.forms import Bootstrap3ModelForm

class ContactForm(Bootstrap3ModelForm):

    class Meta:
        model = Contact  
        fields = ('name', 'email', 'subject', 'message',)
        widgets = {
            'message': forms.Textarea(attrs={'cols': 40, 'rows': 6.5}),
        }
