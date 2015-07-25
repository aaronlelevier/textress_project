import stripe

from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from model_mommy import mommy

from payment.models import StripeClient, Customer, Card, Charge, Refund

# Set Stripe Key for All tests
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeClientTests(TestCase):

    def test_init(self):
        sc = StripeClient()
        self.assertIsInstance(sc, StripeClient)
        self.assertIsNotNone(sc.stripe.api_key)


class CustomerTests(TestCase):

    # fixtures = ['payment.json']

    def setUp(self):
        self.sc = stripe.Customer.all(limit=1)
        self.customer = mommy.make(Customer, id=self.sc.data[0].id)

    def test_create(self):
        self.assertTrue(Customer.objects.count() > 0)

    def test_stripe_attr(self):
        self.assertTrue(hasattr(self.customer, 'stripe'))

    def test_stripe_object_attr(self):
        self.assertTrue(hasattr(self.customer, 'stripe_object'))

    def test_get_all_charges(self):
        self.assertIsNotNone(self.customer.get_all_charges())

