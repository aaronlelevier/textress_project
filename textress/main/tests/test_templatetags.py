from django.core.urlresolvers import reverse
from django.test import TestCase

from main.templatetags.user_tags import has_group, user_has_group
from main.tests.factory import PASSWORD, create_hotel, create_hotel_user
from utils.create import _get_groups_and_perms


class TemplateTagTests(TestCase):

    def setUp(self):
        _get_groups_and_perms()
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel, group='hotel_admin')

    def test_has_group(self):
        self.assertTrue(has_group(self.user, 'hotel_admin'))

    def test_user_has_group(self):
        self.assertFalse(user_has_group(['foo'], 'hotel_admin'))
        self.assertTrue(user_has_group(['hotel_admin'], 'hotel_admin'))
        self.assertTrue(user_has_group(['foo', 'hotel_admin'], 'hotel_admin'))
