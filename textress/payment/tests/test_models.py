import stripe
import pytest
from model_mommy import mommy

from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from payment.models import StripeClient, Customer, Card, Charge, Refund

# Set Stripe Key for All tests
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeClientTests(TestCase):

    def test_init(self):
        sc = StripeClient()
        self.assertIsInstance(sc, StripeClient)
        self.assertIsNotNone(sc.stripe.api_key)


class CustomerTests(TestCase):

    fixtures = ['payment.json']

    def test_fixtures(self):
        # are fixtures loading any Customer records?
        self.assertTrue(Customer.objects.count() > 0)

    def test_stripe_attr(self):
        c = Customer.objects.first()
        print 'id:', c.id
        print c.stripe_object
        self.assertTrue(hasattr(c, 'stripe_object'))