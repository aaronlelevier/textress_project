import os

from django.conf import settings
from django.test import TestCase
from django.core.exceptions import ValidationError

from model_mommy import mommy
from twilio.rest import TwilioRestClient
from twilio.rest.resources.phone_numbers import PhoneNumber as TwilioPhoneNumber

from main.tests.factory import create_hotel
from sms.models import PhoneNumber
from sms.tests.factory import create_phone_number


class PhoneNumberManagerTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.ph = create_phone_number(self.hotel)
        self.ph2 = create_phone_number(self.hotel)

    def test_validate_ph_num(self):
        ph = PhoneNumber.objects._validate_ph_num(self.hotel, self.ph.sid)
        self.assertIsInstance(ph, PhoneNumber)

    def test_validate_ph_num_raise_error(self):
        with self.assertRaises(ValidationError):
            PhoneNumber.objects._validate_ph_num(self.hotel, 'bad-sid')

    def test_set_default(self):
        self.ph.default = False
        self.ph.save()
        # Get PH and confirm it's still ``default=False``
        self.ph = PhoneNumber.objects.get(sid=self.ph.sid)
        self.assertFalse(self.ph.default)
        # Now method will set to ``default=True``
        PhoneNumber.objects._set_default(self.hotel, self.ph.sid)
        self.ph = PhoneNumber.objects.get(sid=self.ph.sid)
        self.assertTrue(self.ph.default)

    def test_update_non_defaults(self):
        # Start out with a default, and after calling this method,
        # that PH should still be the default.
        PhoneNumber.objects._set_default(self.hotel, self.ph.sid)
        PhoneNumber.objects._update_non_defaults(self.hotel, self.ph.sid)
        self.assertTrue(self.ph.default)
        for ph in PhoneNumber.objects.exclude(sid=self.ph.sid):
            self.assertFalse(ph.default)

    def test_update_default(self):
        # ph
        PhoneNumber.objects.update_default(self.hotel, self.ph.sid)
        self.assertTrue(self.ph.default)
        for ph in PhoneNumber.objects.exclude(sid=self.ph.sid):
            self.assertFalse(ph.default)
        # ph2
        PhoneNumber.objects.update_default(self.hotel, self.ph2.sid)
        self.assertTrue(self.ph2.default)
        for ph in PhoneNumber.objects.exclude(sid=self.ph2.sid):
            self.assertFalse(ph.default)

    def test_default(self):
        PhoneNumber.objects.update_default(self.hotel, self.ph.sid)
        default = PhoneNumber.objects.default(self.hotel)
        self.assertTrue(default, PhoneNumber)

    def test_default_no_current_defaults(self):
        self.ph.default = False
        self.ph.save()
        self.ph2.default = False
        self.ph2.save()
        self.assertFalse(PhoneNumber.objects.filter(default=True))
        ph = PhoneNumber.objects.default(self.hotel)
        self.assertIsInstance(ph, PhoneNumber)
        self.assertTrue(ph.default)

    def test_default_multiple_defaults(self):
        self.ph.default = True
        self.ph.save()
        self.ph2.default = True
        self.ph2.save()
        self.assertTrue(PhoneNumber.objects.filter(default=True))
        ph = PhoneNumber.objects.default(self.hotel)
        self.assertIsInstance(ph, PhoneNumber)
        self.assertTrue(ph.default)

    def test_update_account_sid(self):
        # TODO: CONTINUE HERE
        pass

        
    # LIVE TEST
    # def test_twilio_purchase_number(self):
    #     twilio_ph = PhoneNumber.objects._twilio_purchase_number(self.hotel)
    #     self.assertIsInstance(twilio_ph, TwilioPhoneNumber)

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

    def test_default(self):
        hotel = create_hotel()
        phones = mommy.make(PhoneNumber, hotel=hotel, _quantity=3)

        # Need to update the "default" ph num 1st or else ".default()"
        # will return multiple phone numbers
        default = PhoneNumber.objects.default(hotel)
        assert isinstance(default, PhoneNumber)
        assert default.default
        assert len(PhoneNumber.objects.filter(default=False)) == len(phones) - 1


# class LivePhoneNumberTests(TestCase):

#     def setUp(self):
#         self.hotel = create_hotel(name='sub_test_865')

#         # Twilio Test Sid
#         self.test_sid = os.environ['TWILIO_ACCOUNT_SID_TEST']
#         self.test_auth_token = os.environ['TWILIO_AUTH_TOKEN_TEST']
        
#         # Update Hotel Subaccount, so can purchase a PhonNumber
#         self.hotel.update_twilio(sid=self.test_sid,
#             auth_token=self.test_auth_token)

#         self.client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID,
#             settings.TWILIO_AUTH_TOKEN)

#         self.ph_sid = os.environ['TWILIO_TEST_PH_SID']
        
#     def test_purchase_number(self):
#         # # Comment out b/c creates a live Twilio PhoneNumber each time.
#         # number = PhoneNumber.objects.purchase_number(self.hotel)
#         # assert number

#         # Confirm Account Exists
#         dave_acct = self.client.accounts.list(friendly_name='Dave Hotel')[0]
#         assert dave_acct

#         # Confirm that he has a PhoneNumber
#         client = TwilioRestClient(dave_acct.sid, dave_acct.auth_token)
#         dave_number = client.phone_numbers.get(self.ph_sid)
#         assert dave_number

    # def test_update_account_sid(self):
    #     # # First Return PH # to Master Account
    #     # dave_acct = self.client.accounts.list(friendly_name='Dave Hotel')[0]
    #     # client = TwilioRestClient(dave_acct.sid, dave_acct.auth_token)
    #     # number = client.phone_numbers.update(self.ph_sid,
    #     #     account_sid=settings.TWILIO_ACCOUNT_SID)
    #     # assert number.account_sid == settings.TWILIO_ACCOUNT_SID

    #     # Call `update_account_sid`
    #     t_number = self.client.phone_numbers.get(self.ph_sid)
    #     number = PhoneNumber.objects.update_account_sid(self.hotel, t_number)
    #     # Get the Hotel again and confirm the PhoneNumber has been denormalized
    #     hotel = Hotel.objects.get(name='sub_test_865')
    #     assert number.account_sid == self.hotel.sid

    #     # Return the PhoneNubmer to 'Dave Hotel'
    #     dave_acct = self.client.accounts.list(friendly_name='Dave Hotel')[0]
    #     test_client = TwilioRestClient(self.hotel.sid, self.hotel.auth_token)
    #     assert isinstance(test_client, TwilioRestClient)

    #     number = test_client.phone_numbers.update(self.ph_sid,
    #         account_sid=settings.TWILIO_ACCOUNT_SID)