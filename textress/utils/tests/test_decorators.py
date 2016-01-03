from django.core.urlresolvers import reverse
from django.test import TestCase

from main.tests.factory import create_hotel, create_hotel_user, PASSWORD


class LogoutRequiredTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel)

    def test_logged_out(self):
        self.assertNotIn('_auth_user_id', self.client.session)

        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)

    def test_logged_in(self):
        self.client.login(username=self.user.username, password=PASSWORD)

        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)


class LoginRequiredTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel)

    def test_logged_out(self):
        self.assertNotIn('_auth_user_id', self.client.session)

        response = self.client.get(reverse('account'))

        self.assertEqual(response.status_code, 302)

    def test_logged_in(self):
        self.client.login(username=self.user.username, password=PASSWORD)

        response = self.client.get(reverse('account'))

        self.assertEqual(response.status_code, 200)
