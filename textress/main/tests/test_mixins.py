from django.conf import settings
from django.http import Http404
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

from model_mommy import mommy

from concierge.models import Message, Guest
from concierge.tests.factory import make_guests, make_messages
from main import mixins
from main.tests.factory import create_hotel_user, create_hotel, PASSWORD
from utils import create


class HotelMixinTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel)

        # Concierge Models
        self.guests = make_guests(self.hotel, number=1)
        self.guest = self.guests[0]
        self.messages = make_messages(
            hotel=self.hotel,
            user=self.user,
            guest=self.guest,
            number=1
            )
        self.message = self.messages[0]

        # Hotel 2
        self.hotel_b = create_hotel(name='hotel_b')
        self.user_b = create_hotel_user(self.hotel_b, username='user_b')
        self.messages_b = make_messages(
            hotel=self.hotel_b,
            user=self.user_b,
            guest=self.guest,
            number=1
            )
        self.message_b = self.messages_b[0]

    def test_hotel_mixin_auth(self):
        # Logged In - Dave has Access
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(reverse('concierge:message_detail', kwargs={'pk':self.message.pk}))
        self.assertEqual(response.status_code, 200)

    def test_hotel_mixin_non_auth(self):
        self.client.logout()
        with self.assertRaises(PermissionDenied):
            self.client.get(reverse('concierge:message_detail', kwargs={'pk':self.message_b.pk}))


class UserOnlyMixinTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel, group='hotel_admin')
        self.wrong_user = create_hotel_user(self.hotel, username='wrong_user', group='hotel_admin')

    def test_get_wrong_user(self):
        # wrong user can't access another User's Update View
        self.client.login(username=self.wrong_user.username, password=PASSWORD)
        response = self.client.get(reverse('main:user_update', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 403)

    def test_get_right_user(self):
        # wrong user can't access another User's Update View
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(reverse('main:user_update', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)


class HotelAccessMixinTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        # Hotel A
        self.hotel_a = create_hotel(name='hotel_a')
        self.admin_a = create_hotel_user(self.hotel_a, username='admin_a', group='hotel_admin')
        self.user_a = create_hotel_user(self.hotel_a, username='user_a')
        # Hotel B
        self.hotel_b = create_hotel(name='hotel_b')
        self.admin_b = create_hotel_user(self.hotel_b, username='admin_b', group='hotel_admin')
        self.user_b = create_hotel_user(self.hotel_b, username='user_b')

    ### HotelUsersOnlyMixin ###

    def test_HotelUsersOnlyMixin_get_wrong_hotel(self):
        self.client.login(username=self.admin_a.username, password=PASSWORD)
        response = self.client.get(reverse('main:manage_user_update', kwargs={'pk':self.user_b.pk}))
        self.assertEqual(response.status_code, 403)

    def test_HotelUsersOnlyMixin_get_right_hotel(self):
        self.client.login(username=self.admin_a.username, password=PASSWORD)
        response = self.client.get(reverse('main:manage_user_update', kwargs={'pk':self.user_a.pk}))
        self.assertEqual(response.status_code, 200)

    ### MyHotelOnlyMixin ###

    def test_MyHotelOnlyMixin_get_wrong_hotel(self):
        self.client.login(username=self.admin_a.username, password=PASSWORD)
        response = self.client.get(reverse('main:register_step2_update', kwargs={'pk':self.hotel_b.pk}))
        self.assertEqual(response.status_code, 403)

    def test_MyHotelOnlyMixin_get_right_hotel(self):
        self.client.login(username=self.admin_a.username, password=PASSWORD)
        response = self.client.get(reverse('main:register_step2_update', kwargs={'pk':self.hotel_a.pk}))
        self.assertEqual(response.status_code, 200)


class RegistrationContextMixinTests(TestCase):

    def test_context(self):
        response = self.client.get(reverse('main:register_step1'))
        self.assertIsNotNone(response.context['steps'])
