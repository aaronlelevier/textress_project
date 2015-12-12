from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy

from account.models import AcctCost
from concierge.tests.factory import make_guests, make_messages
from main.tests.factory import create_user, create_hotel_user, create_hotel, PASSWORD
from utils import create
from utils.messages import dj_messages, login_messages


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

    ### HotelObjectMixin ###
    
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

    ### MyHotelOnlyMixin ###

    def test_MyHotelOnlyMixin_get_wrong_hotel(self):
        self.client.login(username=self.admin_a.username, password=PASSWORD)
        response = self.client.get(reverse('main:register_step2_update', kwargs={'pk':self.hotel_b.pk}))
        self.assertEqual(response.status_code, 403)

    def test_MyHotelOnlyMixin_get_right_hotel(self):
        self.client.login(username=self.admin_a.username, password=PASSWORD)
        response = self.client.get(reverse('main:register_step2_update', kwargs={'pk':self.hotel_a.pk}))
        self.assertEqual(response.status_code, 200)


class HotelUserMixinTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.user, _ = create_user(group='hotel_admin')

    def test_login_verifier(self):
        self.assertFalse(settings.LOGIN_VERIFIER)

    def test_superusers_exempt(self):
        """
        No extra configuration on ``HotelUserMixin`` needed for the "superuser", 
        if they just go strait to the "django admin" they can access it.
        """
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()

        with self.settings(LOGIN_VERIFIER=True):
            response = self.client.post(reverse('login'),
                {'username': self.user.username, 'password': PASSWORD}, follow=True)

            # Gets redirect to the "CreateHotel" registration step, b/c doesn't 
            # have a Hotel, but from there can go to the "django admin"
            self.assertRedirects(response, reverse('main:register_step2'))
            response = self.client.get('/aronysidoro/')
            self.assertEqual(response.status_code, 200)

    def test_hotel_not_created_redirect(self):
        with self.settings(LOGIN_VERIFIER=True):
            response = self.client.post(reverse('login'),
                {'username': self.user.username, 'password': PASSWORD}, follow=True)

            self.assertRedirects(response, reverse('main:register_step2'))
            m = list(response.context['messages'])
            self.assertEqual(len(m), 2)
            self.assertEqual(str(m[0]), login_messages['now_logged_in'])
            self.assertEqual(str(m[1]), dj_messages['complete_registration'])

    def test_acct_cost_not_created(self):
        hotel = create_hotel()
        hotel.set_admin_id(self.user)

        with self.settings(LOGIN_VERIFIER=True):
            response = self.client.post(reverse('login'),
                {'username': self.user.username, 'password': PASSWORD}, follow=True)

            self.assertRedirects(response, reverse('register_step3'))
            m = list(response.context['messages'])
            self.assertEqual(len(m), 2)
            self.assertEqual(str(m[0]), login_messages['now_logged_in'])
            self.assertEqual(str(m[1]), dj_messages['complete_registration'])

    def test_customer_not_created(self):
        hotel = create_hotel()
        hotel.set_admin_id(self.user)
        mommy.make(AcctCost, hotel=hotel)

        with self.settings(LOGIN_VERIFIER=True):
            response = self.client.post(reverse('login'),
                {'username': self.user.username, 'password': PASSWORD}, follow=True)

            self.assertRedirects(response, reverse('payment:register_step4'))
            m = list(response.context['messages'])
            self.assertEqual(len(m), 2)
            self.assertEqual(str(m[0]), login_messages['now_logged_in'])
            self.assertEqual(str(m[1]), dj_messages['complete_registration'])


class RegistrationContextMixinTests(TestCase):

    def test_context(self):
        response = self.client.get(reverse('main:register_step1'))
        self.assertIsNotNone(response.context['steps'])
