import os

from twilio.rest.client import TwilioRestClient

from django.test import TestCase

from concierge.helpers import process_from_messages
from concierge.models import Message
from concierge.tests.factory import make_guests
from main.models import Hotel
from main.tests.factory import create_hotel


class ProcessFromMessageTests(TestCase):

    def setUp(self):
        # Hotel
        self.hotel = create_hotel()
        self.hotel.twilio_sid = os.environ['TWILIO_ACCOUNT_SID_TEST']
        self.hotel.twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN_TEST']
        self.hotel.save()
        # Guest
        self.guest = make_guests(hotel=self.hotel, number=1)[0]
        self.guest.phone_number = os.environ['TWILIO_PHONE_NUMBER_TEST']
        self.guest.save()

    def test_create(self):
        self.assertIsInstance(self.hotel._client, TwilioRestClient)

    def test_hotel_messages(self):
        self.assertTrue(self.hotel._client.messages.list())

    def test_twilio_message_list(self):
        self.assertTrue(self.hotel._client.messages.list(from_=self.guest.phone_number))

    def test_receive(self):
        # Use the TwilioRestClient for 'aaron hotel', 
        # make sure that I can connect
        # create records in DB that are in Twilio side, but not DB.
        self.assertFalse(Message.objects.exclude(sid__isnull=True))
        process_from_messages()
        self.assertTrue(Message.objects.exclude(sid__isnull=True))
