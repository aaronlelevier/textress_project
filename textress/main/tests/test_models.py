import os
import random

from django.conf import settings
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from django.utils import timezone

from model_mommy import mommy
from twilio.rest import TwilioRestClient

from main.models import TwilioClient, Hotel, UserProfile, Subaccount
from main.tests.factory import create_hotel, create_hotel_user, PASSWORD
from payment.models import Customer
from utils import create


class TwilioClientTests(TestCase):

    def test_client(self):
        tc = TwilioClient()
        self.assertIsInstance(tc, TwilioClient)
        self.assertIsInstance(tc.client, TwilioRestClient)


class HotelTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.password = PASSWORD
        self.hotel = create_hotel()
        self.dave_hotel = create_hotel()
        self.admin = create_hotel_user(self.hotel, group="hotel_admin")
        self.user = create_hotel_user(self.hotel)

    def test_create(self):
        self.assertIsInstance(self.hotel, Hotel)
        self.assertIsInstance(self.user, User)
        self.assertNotEqual(self.hotel.name, self.dave_hotel.name)

    def test_twilio_client(self):
        self.assertIsInstance(self.hotel._client, TwilioRestClient)

    def test_area_code(self):
        self.assertEqual(self.hotel.area_code, self.hotel.address_phone[2:5])

    def test_set_admin_id(self):
        self.hotel.admin_id = None
        self.assertIsNone(self.hotel.admin_id)

        hotel = self.hotel.set_admin_id(self.user)
        self.assertEqual(self.hotel.admin_id, self.user.pk)

    def test_get_admin(self):
        hotel = self.hotel.set_admin_id(self.user)
        self.assertEqual(self.user, self.hotel.get_admin())

    def test_get_admin_none(self):
        self.hotel.admin_id = None
        self.assertIsNone(self.hotel.admin_id)
        self.hotel.save()
        self.assertIsNone(self.hotel.get_admin())

    def test_update_customer(self):
        customer = mommy.make(Customer)
        self.assertIsInstance(customer, Customer)

        hotel = self.hotel.update_customer(customer)
        self.assertEqual(self.hotel.customer, customer)

    def test_update_twilio(self):
        hotel = create_hotel(name='no twilio sid')
        self.assertIsInstance(hotel, Hotel)
        self.assertIsNone(hotel.twilio_sid)
        self.assertIsNone(hotel.twilio_auth_token)

        sid = 'abc'
        hotel = hotel.update_twilio(sid='abc', auth_token='def')
        self.assertIsNotNone(hotel.twilio_sid)
        self.assertIsNotNone(hotel.twilio_auth_token)
        self.assertEqual(hotel.twilio_sid, sid)

    def test_registration_complete(self):
        # Fails b/c existing Hotel doesn't have a Customer
        self.assertFalse(self.hotel.registration_complete)
        # Passes w/ Customer
        customer = mommy.make(Customer)
        self.hotel = self.hotel.update_customer(customer)
        self.assertTrue(self.hotel.registration_complete)

    def test_admin(self):
        self.assertEqual(self.hotel.admin, self.admin)

    def test_get_or_create_subaccount(self):
        with self.assertRaises(Subaccount.DoesNotExist):
            Subaccount.objects.get(hotel=self.hotel)
            
        self.hotel.get_or_create_subaccount()
        self.assertIsInstance(self.hotel.subaccount, Subaccount)

    def test_activate(self):
        self.assertTrue(self.hotel.active)
        self.hotel.active = False
        self.hotel.save()
        self.assertFalse(self.hotel.active)
        self.hotel.activate()
        self.assertTrue(self.hotel.active)

    def test_deactivate(self):
        self.assertTrue(self.hotel.active)
        self.hotel.deactivate()
        self.assertFalse(self.hotel.active)
        

class UserProfileTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.hotel = create_hotel()

    def test_create(self):
        user = mommy.make(User, first_name='Test', last_name='Test')
        user_profile = user.profile
        assert isinstance(user_profile, UserProfile)
        assert str(user_profile) == user_profile.user.username

    def test_delete(self):
        user = mommy.make(User, first_name='Test', last_name='Test')
        user_profiles = UserProfile.objects.all()
        assert len(user_profiles) == 1

        user.delete()
        users = User.objects.all()
        user_profiles = UserProfile.objects.all()
        assert not users
        assert not user_profiles

    def test_manager(self):
        user = mommy.make(User, first_name='Test', last_name='Test')
        user_profiles = UserProfile.objects.all()
        assert len(user_profiles) == 1

        user_profiles = UserProfile.objects.archived()
        assert len(user_profiles) == 0

    def test_is_admin(self):
        admin = create_hotel_user(self.hotel, group='hotel_admin')
        self.assertTrue(admin.profile.is_admin)

    def test_is_manager(self):
        mgr = create_hotel_user(self.hotel, group='hotel_manager')
        self.assertTrue(mgr.profile.is_manager)


class SubaccountTests(TestCase):

    def setUp(self):
        self.password = '1234'
        self.today = timezone.now().date()

        # Twilio Test Sid
        # name='sub_test_865'
        self.test_sid = os.environ['TWILIO_ACCOUNT_SID_TEST']
        self.test_auth_token = os.environ['TWILIO_AUTH_TOKEN_TEST']

        # Hotel
        randint = random.randint(0,1000)
        self.hotel = create_hotel(name="sub_test_{}".format(randint))

        # create "Hotel Manager" Group
        create._get_groups_and_perms()

        # Admin
        self.admin = mommy.make(User, username='admin')
        self.admin.groups.add(Group.objects.get(name="hotel_admin"))
        self.admin.set_password(self.password)
        self.admin.save()
        self.admin.profile.update_hotel(hotel=self.hotel)
        # Hotel Admin ID
        self.hotel.admin_id = self.admin.id
        self.hotel.save()

        self.client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN)

    ### Manager Tests ###

    def test_twilio_connection(self):
        assert isinstance(self.client, TwilioRestClient)

    def test_get(self):
        hotel = Hotel.objects.first()

        # Get
        sub = Subaccount.objects.create(
            hotel=hotel,
            sid=self.test_sid,
            auth_token=self.test_auth_token)
        self.assertIsInstance(sub, Subaccount)

        sub_2, created = Subaccount.objects.get_or_create(hotel=hotel)
        self.assertFalse(created)
        self.assertEqual(sub, sub_2)

        # the DB instance is created, but the Twilio Instance is not
        self.assertEqual(len(self.client.accounts.list(friendly_name=hotel.name)), 0)