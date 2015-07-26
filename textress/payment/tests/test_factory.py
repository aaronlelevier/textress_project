import stripe

from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse

from model_mommy import mommy

from payment.models import StripeClient, Customer, Card, Charge, Refund
from payment.tests import factory


# Set Stripe Key for All tests
stripe.api_key = settings.STRIPE_SECRET_KEY


class CustomerTests(TestCase):

    def test_stripe_customer(self):
        sc = factory.stripe_customer()
        self.assertIsNotNone(sc.id)

    def test_customer(self):
        self.assertIsInstance(factory.customer(), Customer)


class CardTests(TestCase):

    def test_stripe_card(self):
        sc = factory.stripe_card()
        self.assertIsNotNone(sc.id)

    def test_card(self):
        self.assertIsInstance(factory.card(), Card)


class ChargeTests(TestCase):

    def test_stripe_charge(self):
        sc = factory.stripe_charge()
        self.assertIsNotNone(sc.id)

    def test_card(self):
        self.assertIsInstance(factory.charge(), Charge)


class RefundTests(TestCase):

    def test_stripe_refund(self):
        sr = factory.stripe_refund()
        if sr:
            self.assertIsNotNone(sr.id)
        else:
            self.assertIsNone(sr)