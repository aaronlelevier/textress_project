import re

from django import forms
from django.contrib.auth.models import Group
from django.utils.translation import ugettext, ugettext_lazy as _

from .forms import EmptyForm
from .messages import dj_messages
from .mixins import DeleteButtonMixin


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


def add_group(user, group):
    group = Group.objects.get(name=group)
    user.groups.add(group)
    user.save()
    return user