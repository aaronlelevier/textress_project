from __future__ import absolute_import

import re

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.utils.translation import ugettext, ugettext_lazy as _

from .forms import EmptyForm
from .helpers import salt
from .messages import dj_messages, login_messages
from .mixins import DeleteButtonMixin

__all__ = [
    'DeleteButtonMixin',
    'dj_messages',
    'login_messages',
    'EmptyForm',
    'salt'
]


def validate_phone(phone):
    '''Return: valid Twilio PH #. i.e. '+17025101234'
        else raise Form Error.'''

    error_messages = {
        'invalid_ph':_('Please enter a 10-digit phone number'),
    }
    try:
        r = re.compile(r"[^\d]")
        re_phone = re.search(r'\d{10}$', r.sub("", phone)).group()
    except AttributeError:
        raise ValidationError(error_messages['invalid_ph'])
    else:
        return "+1"+re_phone


def ph_formatter(phone):
    '''
    `pre`: len(phone) == 10
    
    `post`: 10 10-digit ph num spaced for ex: 702-510-1234
    '''
    phone = validate_phone(phone)
    return phone[2:5]+'-'+phone[5:8]+'-'+phone[8:]


def add_group(user, group):
    group = Group.objects.get(name=group)
    user.groups.add(group)
    user.save()
    return user