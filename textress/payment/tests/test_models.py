import stripe

from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse

from model_mommy import mommy

from payment.models import StripeClient, Customer, Card, Charge, Refund
from payment.tests import factory

# Set Stripe Key for All tests
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeClientTests(TestCase):

    def test_init(self):
        sc = StripeClient()
        self.assertIsInstance(sc, StripeClient)
        self.assertIsNotNone(sc.stripe.api_key)


class CustomerTests(TestCase):

    def setUp(self):
        self.customer = factory.customer()

    def test_stripe_attr(self):
        self.assertTrue(hasattr(self.customer, 'stripe'))

    def test_stripe_object_attr(self):
        self.assertTrue(hasattr(self.customer, 'stripe_object'))

    def test_get_all_charges(self):
        self.assertIsNotNone(self.customer.get_all_charges())


class CardTests(TestCase):

    def setUp(self):
        self.card = factory.card()

    def test_stripe_object_attr(self):
        self.assertTrue(hasattr(self.card, 'stripe_object'))

    def test_get_absolute_url(self):
        self.assertEqual(
            self.card.get_absolute_url(),
            reverse('payment:card_detail', kwargs={'pk': self.card.short_pk})
        )

    def test_expires(self):
        self.assertIsInstance(self.card.expires, str)


class ChargeTests(self):
    




