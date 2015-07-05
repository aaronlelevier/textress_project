import os
import random

from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.utils import timezone

from model_mommy import mommy
from twilio.rest import TwilioRestClient

from main.models import TwilioClient, Hotel, UserProfile, Subaccount
from main.tests.factory import create_hotel, create_hotel_user
from payment.models import Customer
from utils import create
from utils.data import STATES


class TwilioClientTests(TestCase):

    def test_client(self):
        tc = TwilioClient()
        self.assertIsInstance(tc, TwilioClient)
        self.assertIsInstance(tc.client, TwilioRestClient)


class HotelManagerTests(TestCase):

    fixtures = ['users.json', 'main.json', 'sms.json', 'payment.json']

    def setUp(self):
        create._get_groups_and_perms()
        self.password = '1234'

        # set User "aaron_test" from fixtures as an attr on this class
        self.user = User.objects.get(username='aaron_test')
        # b/c passwords are stored as a hash in json fixtures
        self.user.set_password(self.password)
        self.user.save()

        self.username = self.user.username
        self.hotel = self.user.profile.hotel

        # Phone
        self.ph_num = self.hotel.phonenumbers.primary(hotel=self.hotel)

    def test_get_by_phone(self):
        hotel = Hotel.objects.get_by_phone(self.hotel.address_phone)
        self.assertTrue(isinstance(hotel, Hotel))

    def test_get_by_phone_fail(self):
        # should return the Textres Hotel default object
        hotel = Hotel.objects.get_by_phone('1') #invalid ph num
        self.assertEqual(hotel, Hotel.objects.get(name=settings.TEXTRESS_HOTEL))

    def test_textress(self):
        # default Hotel object
        hotel = Hotel.objects.textress()
        self.assertTrue(isinstance(hotel, Hotel))
        self.assertEqual(hotel.name, settings.TEXTRESS_HOTEL)


class HotelTests(TestCase):

    fixtures = ['users.json', 'main.json', 'sms.json', 'payment.json']

    def setUp(self):
        self.password = '1234'
        self.hotel = Hotel.objects.first()
        self.dave_hotel = Hotel.objects.get(name=settings.TEXTRESS_HOTEL)

        self.user = User.objects.create_user('Test', settings.DEFAULT_FROM_EMAIL, self.password)
        self.user.set_password(self.password)
        self.user.save()
        self.user_profile = self.user.profile
        self.user_profile.update_hotel(self.dave_hotel)

    def test_create(self):
        self.assertNotEqual(self.hotel.name, self.dave_hotel.name)
        self.assertTrue(isinstance(self.dave_hotel, Hotel))
        self.assertTrue(isinstance(self.user, User))

    def test_twilio_client(self):
        assert isinstance(self.dave_hotel._client, TwilioRestClient)

    def test_area_code(self):
        assert self.hotel.area_code == '210'

    def test_set_admin_id(self):
        self.hotel.admin_id = None
        assert not self.hotel.admin_id

        hotel = self.hotel.set_admin_id(self.user)
        assert self.hotel.admin_id == self.user.pk

    def test_update_customer(self):
        customer = mommy.make(Customer)
        assert isinstance(customer, Customer)

        hotel = self.hotel.update_customer(customer)
        assert self.hotel.customer == customer

    def test_update_twilio(self):
        hotel = create_hotel(name='no twilio sid')
        assert isinstance(hotel, Hotel)
        assert not hotel.twilio_sid
        assert not hotel.twilio_auth_token

        hotel.update_twilio(sid='abc', auth_token='def')
        assert hotel.twilio_sid
        assert hotel.twilio_auth_token

    def test_is_textress(self):
        textress, created = Hotel.objects.get_or_create(name=settings.TEXTRESS_HOTEL)
        self.assertTrue(textress.is_textress)
        

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