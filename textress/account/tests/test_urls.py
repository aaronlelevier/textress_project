from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy

from account.models import AcctCost
from account.tests.factory import create_acct_stmt
from main.tests.factory import create_hotel, create_hotel_user, PASSWORD
from utils import create
from utils.models import Dates


class UrlAuthTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel, group='hotel_admin')

    # register_patterns

    def test_register_step3(self):
        self.client.login(username=self.user.username, password=PASSWORD)

        response = self.client.get(reverse('register_step3'))

        self.assertEqual(response.status_code, 200)

    def test_register_step3__logged_out(self):
        response = self.client.get(reverse('register_step3'))

        self.assertEqual(response.status_code, 302)

    def test_register_step3_update(self):
        self.acct_cost = mommy.make(AcctCost, hotel=self.hotel)
        self.client.login(username=self.user.username, password=PASSWORD)

        response = self.client.get(reverse('register_step3_update',
            kwargs={'pk': self.acct_cost.hotel.pk}))

        self.assertEqual(response.status_code, 200)

    def test_register_step3_update__logged_out(self):
        self.acct_cost = mommy.make(AcctCost, hotel=self.hotel)
        self.client.login(username=self.user.username, password=PASSWORD)
        self.client.logout()

        response = self.client.get(reverse('register_step3_update',
            kwargs={'pk': self.acct_cost.hotel.pk}))

        self.assertEqual(response.status_code, 302)

    # api_patterns - No Permissions required

    # acct_cost_patterns

    def test_acct_cost_update(self):
        self.acct_cost = mommy.make(AcctCost, hotel=self.hotel)
        self.client.login(username=self.user.username, password=PASSWORD)

        response = self.client.get(reverse('acct_cost_update',
            kwargs={'pk': self.acct_cost.hotel.pk}))

        self.assertEqual(response.status_code, 200)

    def test_acct_cost_update__logged_out(self):
        self.acct_cost = mommy.make(AcctCost, hotel=self.hotel)
        self.client.login(username=self.user.username, password=PASSWORD)
        self.client.logout()

        response = self.client.get(reverse('acct_cost_update',
            kwargs={'pk': self.acct_cost.hotel.pk}))

        self.assertEqual(response.status_code, 302)

    def test_acct_pmt_history(self):
        self.acct_cost = mommy.make(AcctCost, hotel=self.hotel)
        self.client.login(username=self.user.username, password=PASSWORD)

        response = self.client.get(reverse('acct_pmt_history'))

        self.assertEqual(response.status_code, 200)

    def test_acct_pmt_history__logged_out(self):
        self.acct_cost = mommy.make(AcctCost, hotel=self.hotel)
        self.client.login(username=self.user.username, password=PASSWORD)
        self.client.logout()

        response = self.client.get(reverse('acct_pmt_history'))

        self.assertEqual(response.status_code, 302)

    # acct_stmt_patterns

    def test_acct_stmt_detail(self):
        today = Dates()._today
        year = today.year
        month = today.month
        acct_stmt = create_acct_stmt(self.hotel, year, month)
        self.client.login(username=self.user.username, password=PASSWORD)

        response = self.client.get(reverse('acct_stmt_detail',
            kwargs={'year': year, 'month': month}))

        self.assertEqual(response.status_code, 200)

    def test_acct_stmt_detail__logged_out(self):
        today = Dates()._today
        year = today.year
        month = today.month
        acct_stmt = create_acct_stmt(self.hotel, year, month)

        response = self.client.get(reverse('acct_stmt_detail',
            kwargs={'year': year, 'month': month}))

        self.assertEqual(response.status_code, 302)

    # account_patterns

    def test_login(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)

    def test_login__logged_in(self):
        self.client.login(username=self.user.username, password=PASSWORD)

        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 302)

    def test_account(self):
        response = self.client.get(reverse('account'))

        self.assertEqual(response.status_code, 302)

    def test_account__logged_in(self):
        self.client.login(username=self.user.username, password=PASSWORD)

        response = self.client.get(reverse('account'))

        self.assertEqual(response.status_code, 200)
