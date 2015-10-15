from django.test import TestCase
from django.contrib.auth.models import User

from main.models import Hotel, UserProfile
from main.tests import factory
from utils import create


class FactoryTests(TestCase):

    def setUp(self):
        # create Groups
        create._get_groups_and_perms()

    def test_create_hotel(self):
        hotel = factory.create_hotel()
        self.assertIsInstance(hotel, Hotel)

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

    def test_create_hotel_random_name(self):
        hotel = factory.create_hotel()
        hotel2 = factory.create_hotel()
        self.assertNotEqual(hotel.name, hotel2.name)

    def test_create_hotel_random_address_phone(self):
        hotel = factory.create_hotel()
        hotel2 = factory.create_hotel()
        self.assertNotEqual(hotel.address_phone, hotel2.address_phone)
