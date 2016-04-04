import os

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User, Group

from django.core.cache import get_cache
cache = get_cache('default')

from model_mommy import mommy
from twilio.rest import TwilioRestClient
from twilio.rest.resources.messages import Message as TwilioMessage
from concierge.models import Message
from main.tests.test_models import create_hotel
from sms.helpers import send_text, send_message
from utils import create


class SendMessageTests(TestCase):

    def setUp(self):
        self.password = '1234'
        self.hotel = create_hotel()
        self.hotel.twilio_sid = os.environ['TWILIO_ACCOUNT_SID_TEST']
        self.hotel.twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN_TEST']
        self.hotel.twilio_phone_number = os.environ['TWILIO_PHONE_NUMBER_TEST']
        self.hotel.save()

    def test_send_message(self):
        message = send_message(hotel=self.hotel, to=settings.DEFAULT_TO_PH,
            body='sms.test.test_helpers msg')
        self.assertTrue(message)

    def test_send_message_increments_redis_sms_count(self):
        cache.delete(self.hotel.redis_key)

        message = send_message(hotel=self.hotel, to=settings.DEFAULT_TO_PH,
            body='sms.test.test_helpers msg')

        self.assertEqual(cache.get(self.hotel.redis_key), 1)
