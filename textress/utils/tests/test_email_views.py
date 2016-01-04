from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy

from account.models import AcctCost
from main.tests.factory import create_hotel, create_hotel_user
from payment.tests.factory import fake_charge


class EmailViewTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel)
        self.charge = fake_charge()
        self.acct_cost = mommy.make(AcctCost, hotel=self.hotel)

    def test_renders(self):
        response = self.client.get(reverse('email_views:index'))

        self.assertEqual(response.status_code, 200)
        self.assertIn("account_charged", response.content)
        self.assertIn("auto_recharge_failed", response.content)

    def test_base_template(self):
        response = self.client.get(reverse('email_views:account_charged'))

        self.assertIn(settings.DEFAULT_EMAIL_BILLING, response.content)
        self.assertIn(settings.TEXTRESS_PHONE_NUMBER, response.content)

    def test_account_charged(self):
        response = self.client.get(reverse('email_views:account_charged'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], self.user)
        # charge
        self.assertEqual(response.context['charge'], self.charge)
        self.assertIn(self.charge.short_pk, response.content)
        self.assertIn(self.charge.created.strftime("%b. %-d, %Y"), response.content)
        self.assertIn("${:.2f}".format(self.charge.amount/100.0), response.content)

    def test_auto_recharge_failed(self):
        response = self.client.get(reverse('email_views:auto_recharge_failed'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], self.user)
        self.assertEqual(response.context['hotel'], self.hotel)
        self.assertIn(settings.SITE_URL, response.content)
        # urls
        self.assertIn(reverse('acct_cost_update', kwargs={'pk': self.acct_cost.pk}), response.content)
        self.assertIn(reverse('payment:one_time_payment'), response.content)


