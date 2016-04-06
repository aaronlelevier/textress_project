import os

from django.test import TestCase

from twilio.rest.client import TwilioRestClient

from account.models import Dates
from concierge import helpers
from concierge.models import Message
from concierge.tests.factory import make_guests, make_messages
from main.models import Hotel
from main.tests.factory import create_hotel, create_hotel_user


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
        # User
        self.user = create_hotel_user(self.hotel)
        # Dates
        self.today = Dates()._today

    def test_create(self):
        self.assertIsInstance(self.hotel._client, TwilioRestClient)

    def test_twilio_message(self):
        # Direct Twilio API call
        self.assertIsInstance(self.hotel._client.messages.list(from_=self.guest.phone_number), list)

    def test_guest_twilio_messages(self):
        # Helper Method that calls Twilio API
        self.assertIsInstance(helpers.guest_twilio_messages(self.guest, self.today), list)

    def test_merge_twilio_messages_to_db(self):
        # Create 1 Msg, and then run: ``merge_twilio_messages_to_db`` this should only 
        # return new Messages, so count = All - 1 (for the Msg that was already created)
        
        # Setup
        self.assertEqual(Message.objects.count(), 0)
        make_messages(self.hotel, self.user, self.guest, number=1)
        self.assertEqual(Message.objects.count(), 1)
        # test
        messages = helpers.merge_twilio_messages_to_db(self.guest, self.today)
        self.assertEqual(
            Message.objects.count() - 1,
            len(messages)
        )

    def test_get_by_phone(self):
        hotel = helpers.get_hotel_by_twilio_phone(self.hotel.twilio_phone_number)
        self.assertTrue(isinstance(hotel, Hotel))

    def test_get_by_phone_fail(self):
        hotel = helpers.get_hotel_by_twilio_phone('1') #invalid ph num
        self.assertIsNone(hotel)

    # ``merge_twilio_messages_to_db_all`` - no test b/c simple forloop


