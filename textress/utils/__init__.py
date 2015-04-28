import re

from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _


def validate_phone(phone):
    '''Return: valid Twilio PH #. i.e. '+17025101234'
        else raise Form Error.'''

    error_messages = {
        'invalid_ph':_('Please enter a 10-digit phone number'),
    }
    try:
        re_phone = re.search(r'\d{10}$', phone).group()
    except AttributeError:
        raise forms.ValidationError(error_messages['invalid_ph'])
    else:
        phone = "+1"+re_phone
    return phone