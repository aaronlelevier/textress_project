import pytest

from django import forms
from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse

from model_mommy import mommy

from sms.forms import PhoneNumberForm, PhoneNumberAddForm
from sms.helpers import sms_messages, bad_ph_error
from utils.exceptions import DailyLimit


class PhoneNumberFormTests(TestCase):
    # TODO
    pass