from django.test import TestCase
from django.contrib.auth.models import User

from twilio import TwilioRestException
from twilio.rest import TwilioRestClient

from main.models import Hotel, UserProfile, Subaccount
from main.tests import factory
from utils import create


class FactoryTests(TestCase):

    def setUp(self):
        # create Groups
        create._get_groups_and_perms()

    def test_create_hotel(self):
        hotel = factory.create_hotel()
        self.assertIsInstance(hotel, Hotel)

    # create_hotel_user

    def test_create_hotel_user_user(self):
        hotel = factory.create_hotel()
        user = factory.create_hotel_user(hotel)
        self.assertIsInstance(user, User)

    def test_create_hotel_user_manager(self):
        group = 'hotel_manager'
        hotel = factory.create_hotel()
        user = factory.create_hotel_user(hotel, group=group)
        self.assertIsInstance(user, User)
        self.assertIsNotNone(user.groups.filter(name=group))

    def test_create_hotel_user_admin(self):
        group = 'hotel_admin'
        hotel = factory.create_hotel()
        user = factory.create_hotel_user(hotel, group=group)
        self.assertIsInstance(user, User)
        self.assertIsNotNone(user.groups.filter(name=group))
        self.assertEqual(hotel.admin_id, user.id)
        self.assertEqual(hotel, user.profile.hotel)

    # create_user

    def test_create_user(self):
        # With a Group
        group_name = 'hotel_admin'
        user, group = factory.create_user(group=group_name)
        self.assertIsInstance(user, User)
        self.assertIn(group, user.groups.all())
        # can login
        self.client.login(username=user.username, password=factory.PASSWORD)
        self.assertIn('_auth_user_id', self.client.session)

    def test_create_user_no_group(self):
        user, group = factory.create_user()
        self.assertIsInstance(user, User)
        self.assertFalse(user.groups.all())
        self.assertIsNone(group)
        # can login
        self.client.login(username=user.username, password=factory.PASSWORD)
        self.assertIn('_auth_user_id', self.client.session)

    def test_create_hotel_random_name(self):
        hotel = factory.create_hotel()
        hotel2 = factory.create_hotel()
        self.assertNotEqual(hotel.name, hotel2.name)

    def test_create_hotel_random_address_phone(self):
        hotel = factory.create_hotel()
        hotel2 = factory.create_hotel()
        self.assertNotEqual(hotel.address_phone, hotel2.address_phone)

    def test_make_subaccount_live(self):
        hotel = factory.create_hotel()
        sub = factory.make_subaccount(hotel, live=True)
        self.assertIsInstance(sub, Subaccount)
        self.assertTrue(sub.twilio_object)
        self.assertIsInstance(sub.client, TwilioRestClient)

    def test_make_subaccount_not_live(self):
        hotel = factory.create_hotel()
        sub = factory.make_subaccount(hotel)
        self.assertIsInstance(sub, Subaccount)

        with self.assertRaises(TwilioRestException):
            self.assertTrue(sub.twilio_object)
