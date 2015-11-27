from django.conf import settings
from django.test import TestCase, TransactionTestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from model_mommy import mommy

from account.models import AcctCost, CHARGE_AMOUNTS, BALANCE_AMOUNTS
from account.tests.factory import create_acct_stmts, create_acct_trans
from main.tests.factory import create_hotel, create_hotel_user, PASSWORD
from sms.models import PhoneNumber
from utils import create, login_messages


class AuthTests(TestCase):

    def setUp(self):
        # Groups
        create._get_groups_and_perms()
        # User
        self.password = '1234'
        self.user = User.objects.create_user('Bobby',
            settings.DEFAULT_FROM_EMAIL, self.password)
        # add Hotel
        self.hotel = create_hotel()
        self.user.profile.update_hotel(self.hotel)

    def test_login(self):
        response = self.client.get(reverse('logout'))
        with self.assertRaises(TypeError):
            assert response.context['user'].username != self.user.username

        response = self.client.post(reverse('login'),
                        {'username': self.user,
                        'password': self.password}, follow=True)
        self.assertRedirects(response, reverse('account'))
        assert response.context['user'].username == self.user.username
        # login success message rendered
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        self.assertEqual(str(m[0]), login_messages['now_logged_in'])

    def test_logout(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('logout'))
        assert response.status_code == 302
        with self.assertRaises(TypeError):
            assert not response.context['user']


class PasswordChangeFormTests(TestCase):

    def setUp(self):
        self.password = PASSWORD
        self.new_password = '2222'
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel)
        # Login
        self.client.login(username=self.user.username, password=self.password)

    def test_get(self):
        response = self.client.post(reverse('password_change'))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        # change password
        response = self.client.post(reverse('password_change'),
            {'old_password': self.password,
            'new_password1': self.new_password,
            'new_password2': self.new_password
            }, follow=True)
        self.assertRedirects(response, reverse('password_change_done'))
        response = self.client.get(reverse('logout'))
        
        # login w/ new password
        response = self.client.post(reverse('login'),
                        {'username': self.user,
                        'password': self.new_password}, follow=True)
        self.assertRedirects(response, reverse('account'))
        assert response.context['user'].username == self.user.username


class AcctCostUpdateTests(TransactionTestCase):

    fixtures = ['trans_type.json']

    def setUp(self):
        self.password = PASSWORD
        self.hotel = create_hotel()

        # create "Hotel Manager" Group
        create._get_groups_and_perms()

        # Users
        self.admin = create_hotel_user(hotel=self.hotel, username='admin', group='hotel_admin')
        self.user = create_hotel_user(hotel=self.hotel, username='user')

        self.client.login(username=self.admin.username, password=PASSWORD)

        # Billing Stmt Fixtures
        self.acct_cost, created = AcctCost.objects.get_or_create(self.hotel)
        self.acct_stmts = create_acct_stmts(self.hotel)
        self.acct_trans = create_acct_trans(self.hotel)
        self.phone_number = mommy.make(PhoneNumber, hotel=self.hotel)

    def test_acct_cost_update_get(self):
        response = self.client.get(reverse('acct_cost_update', kwargs={'pk': self.acct_cost.pk}))
        self.assertEqual(response.status_code, 200)

    def test_acct_cost_update_post(self):
        data = {
            'balance_min': BALANCE_AMOUNTS[0][0],
            'recharge_amt': CHARGE_AMOUNTS[0][0],
            'auto_recharge': True
        }
        response = self.client.post(reverse('acct_cost_update', kwargs={'pk': self.acct_cost.pk}),
            data, follow=True)
        self.assertRedirects(response, reverse('payment:summary'))