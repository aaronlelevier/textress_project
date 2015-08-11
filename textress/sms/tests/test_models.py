import os
import pytest
from twilio.rest import TwilioRestClient

from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

from model_mommy import mommy

from main.models import Hotel
from main.tests.factory import create_hotel
from sms.models import PhoneNumber
from sms.tests.factory import create_phone_number


class PhoneNumberManagerTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.ph = create_phone_number(self.hotel)
        self.ph2 = create_phone_number(self.hotel)

    def test_create(self):
        pass


class PhoneNumberTests(TestCase):

    def test_default(self):
        ph = create_phone_number()
        self.assertTrue(ph.default)

    def test_last_created_default(TestCase):
        hotel = create_hotel()
        ph = mommy.make(PhoneNumber, hotel=hotel)
        ph_2 = mommy.make(PhoneNumber, hotel=hotel)
        assert ph_2.default

    def test_last_created_default_else(TestCase):
        # Unless expicitly told
        hotel = create_hotel()
        ph = mommy.make(PhoneNumber, hotel=hotel)
        ph_2 = mommy.make(PhoneNumber, hotel=hotel, default=False)
        assert not ph_2.default 

    def test_primary(self):
        hotel = create_hotel()
        phones = mommy.make(PhoneNumber, hotel=hotel, _quantity=3)

        # Need to update the "primary" ph num 1st or else ".primary()"
        # will return multiple phone numbers
        primary = PhoneNumber.objects.primary(hotel)
        assert isinstance(primary, PhoneNumber)
        assert primary.default
        assert len(PhoneNumber.objects.filter(default=False)) == len(phones) - 1


class LivePhoneNumberTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel(name='sub_test_865')

        # Twilio Test Sid
        self.test_sid = os.environ['TWILIO_ACCOUNT_SID_TEST']
        self.test_auth_token = os.environ['TWILIO_AUTH_TOKEN_TEST']
        
        # Update Hotel Subaccount, so can purchase a PhonNumber
        self.hotel.update_twilio(sid=self.test_sid,
            auth_token=self.test_auth_token)

        self.client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN)

        self.ph_sid = os.environ['TWILIO_TEST_PH_SID']
        
    def test_purchase_number(self):
        # # Comment out b/c creates a live Twilio PhoneNumber each time.
        # number = PhoneNumber.objects.purchase_number(self.hotel)
        # assert number

        # Confirm Account Exists
        dave_acct = self.client.accounts.list(friendly_name='Dave Hotel')[0]
        assert dave_acct

        # Confirm that he has a PhoneNumber
        client = TwilioRestClient(dave_acct.sid, dave_acct.auth_token)
        dave_number = client.phone_numbers.get(self.ph_sid)
        assert dave_number

    def test_update_account_sid(self):
        # # First Return PH # to Master Account
        # dave_acct = self.client.accounts.list(friendly_name='Dave Hotel')[0]
        # client = TwilioRestClient(dave_acct.sid, dave_acct.auth_token)
        # number = client.phone_numbers.update(self.ph_sid,
        #     account_sid=settings.TWILIO_ACCOUNT_SID)
        # assert number.account_sid == settings.TWILIO_ACCOUNT_SID

        # Call `update_account_sid`
        t_number = self.client.phone_numbers.get(self.ph_sid)
        number = PhoneNumber.objects.update_account_sid(self.hotel, t_number)
        # Get the Hotel again and confirm the PhoneNumber has been denormalized
        hotel = Hotel.objects.get(name='sub_test_865')
        assert number.account_sid == self.hotel.sid

        # Return the PhoneNubmer to 'Dave Hotel'
        dave_acct = self.client.accounts.list(friendly_name='Dave Hotel')[0]
        test_client = TwilioRestClient(self.hotel.sid, self.hotel.auth_token)
        assert isinstance(test_client, TwilioRestClient)

        number = test_client.phone_numbers.update(self.ph_sid,
            account_sid=settings.TWILIO_ACCOUNT_SID)