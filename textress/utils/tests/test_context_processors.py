from django.core.urlresolvers import reverse
from django.test import TestCase

from main.tests.factory import PASSWORD, create_hotel, create_hotel_user
from utils.create import _get_groups_and_perms


class UserGroupTests(TestCase):

    def test_no_user_groups(self):
        response = self.client.get(reverse('login'))

        self.assertFalse(response.context['user_groups'])

    def test_has_user_groups(self):
        _get_groups_and_perms()
        hotel = create_hotel()
        user = create_hotel_user(hotel, group='hotel_admin')

        response = self.client.post(reverse('login'),
            {'username': user.username, 'password': PASSWORD}, follow=True)

        # import pdb;pdb.set_trace()
        self.assertRedirects(response, reverse('account'))
        self.assertIn('hotel_admin', response.context['user_groups'])
