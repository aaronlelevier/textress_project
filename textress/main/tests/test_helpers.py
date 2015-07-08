from django.test import TestCase
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser

from main.helpers import get_user_hotel
from main.tests.factory import create_hotel, create_hotel_user


class HelperTests(TestCase):

    def test_get_user_hotel_ok(self):
        hotel = create_hotel()
        user = create_hotel_user(hotel)
        self.assertEqual(hotel, get_user_hotel(user))

    def test_get_user_hotel_raises(self):
        with self.assertRaises(PermissionDenied):
            get_user_hotel(AnonymousUser)