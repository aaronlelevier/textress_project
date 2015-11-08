from django.test import TestCase
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser, Group

from main.helpers import get_user_hotel, user_in_group
from main.tests.factory import create_hotel, create_hotel_user
from utils.create import _get_groups_and_perms


class HelperTests(TestCase):

    def test_get_user_hotel_ok(self):
        hotel = create_hotel()
        user = create_hotel_user(hotel)
        self.assertEqual(hotel, get_user_hotel(user))

    def test_get_user_hotel_raises(self):
        with self.assertRaises(PermissionDenied):
            get_user_hotel(AnonymousUser)

    def test_user_in_group_true(self):
        _get_groups_and_perms()
        hotel = create_hotel()
        user = create_hotel_user(hotel, group='hotel_admin')
        self.assertIn('hotel_admin', user.groups.values_list('name', flat=True))

        ret = user_in_group(user, 'hotel_admin')

        self.assertTrue(ret)

    def test_user_in_group_false(self):
        _get_groups_and_perms()
        hotel = create_hotel()
        user = create_hotel_user(hotel)
        self.assertNotIn('hotel_admin', user.groups.values_list('name', flat=True))

        ret = user_in_group(user, 'hotel_admin')

        self.assertFalse(ret)
