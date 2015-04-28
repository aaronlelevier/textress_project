import pytest
import twilio

from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now

from model_mommy import mommy

from sms.models import Text, DemoCounter
from sms.helpers import sms_messages


class ViewTests(TestCase):

    def test_DemoView_bad_number(self):
        """
        Extra Message test methods are for example of different working ways
        to test Django Messages.
        """
        response = self.client.post(reverse('sms:demo'),
            {'to': settings.DEFAULT_TO_PH_BAD},
            follow=True)
        m = list(response.context['messages'])
        assert len(m) != 0
        self.assertRedirects(response, reverse('sms:demo'))
        self.assertEqual(m[0].message, sms_messages['send_failed'])
        assert "SMS failed to send" in m[0].message
        assert "SMS failed to send" in str(m[0])

    def test_DemoView_post(self):
        response = self.client.post(reverse('sms:demo'),
            {'to': settings.DEFAULT_TO_PH},
            follow=True)
        m = list(response.context['messages'])
        assert response.status_code == 200        
        assert len(m) != 0
        self.assertEqual(m[0].message, sms_messages['sent'])

    def test_DemoView_limit_reached(self):
        # preset ``dc`` limit reached counter
        dc = mommy.make(DemoCounter, count=settings.SMS_LIMIT)

        # form submission should fail because ``dc`` limit reached for the day
        response = self.client.post(reverse('sms:demo'),
            {'to': settings.PHONE_NUMBER})

        # ``dc`` counts should be the same, b/c submission failed
        dc_now = DemoCounter.objects.today()
        assert dc.count == dc_now.count