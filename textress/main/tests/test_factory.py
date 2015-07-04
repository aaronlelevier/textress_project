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