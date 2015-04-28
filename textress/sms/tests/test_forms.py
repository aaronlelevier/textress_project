import pytest

from django import forms
from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse

from model_mommy import mommy

from sms.models import Text, DemoCounter
from sms.forms import DemoForm
from sms.helpers import sms_messages, bad_ph_error
from utils.exceptions import DailyLimit


class DemoFormTests(TestCase):
    
    def test_get(self):
        response = self.client.get(reverse('sms:demo'))
        assert isinstance(response.context['form'], DemoForm)

    def test_good_number(self):
        # start with no counts
        no_dc = DemoCounter.objects.delete_all()

        # submit form correctly
        data = {'to': settings.DEFAULT_TO_PH}
        response = self.client.post(reverse('sms:demo'), data)
        # assert response.status_code == 200

        # now there is one record in the DB b/c the form created a ``dc``
        dc = DemoCounter.objects.today()
        assert isinstance(dc, DemoCounter)
        assert dc.count == 1

    def test_bad_number(self):
        data = {'to': "abc"}
        response = self.client.post(reverse('sms:demo'), data=data)
        self.assertFormError(response, 'form', None, [bad_ph_error(data['to'])])

    def test_daily_limit(self):
        # set limit to the send limit for the day
        dc = mommy.make(DemoCounter, count=settings.SMS_LIMIT)
        data = {'to': settings.DEFAULT_TO_PH}

        # try to submit a SMS. Should fail because limit reached
        response = self.client.post(reverse('sms:demo'), data)
        assert response.status_code == 200

        form = DemoForm(data=data)
        assert form.is_valid() == False
        # for form error testing when the error is not attached to a field
        self.assertContains(response, sms_messages['limit_reached'], 1, 200)

        dc_now = DemoCounter.objects.today()
        assert dc.count == dc_now.count