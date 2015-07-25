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

    def setUp(self):
        self.sc = stripe.Customer.all(limit=1)
        self.customer = mommy.make(Customer, id=self.sc.data[0].id)

    def test_create(self):
        self.assertTrue(Customer.objects.count() > 0)
        self.assertIsInstance(self.customer, Customer)

    def test_stripe_attr(self):
        self.assertTrue(hasattr(self.customer, 'stripe'))

    def test_stripe_object_attr(self):
        self.assertTrue(hasattr(self.customer, 'stripe_object'))

    def test_get_all_charges(self):
        self.assertIsNotNone(self.customer.get_all_charges())


class CardTests(TestCase):

    def setUp(self):
        # Stripe Objects
        customer = stripe.Customer.retrieve(stripe.Customer.all(limit=1).data[0].id) # retrieve by id
        card = customer.sources.retrieve(customer.cards.data[0].id) # retrieve by id
        # Textress
        self.customer = mommy.make(Customer, id=customer.id)
        self.card = Card.objects.create(
            customer=self.customer,
            id=card.id,
            brand=card.brand,
            last4=card.last4,
            exp_month=card.exp_month,
            exp_year=card.exp_year
        )

    def test_create(self):
        self.assertIsInstance(self.card, Card)

    def test_stripe_attr(self):
        self.assertTrue(hasattr(self.card, 'stripe'))

    def test_stripe_object_attr(self):
        self.assertTrue(hasattr(self.card, 'stripe_object'))

    def test_get_absolute_url(self):
        self.assertEqual(
            self.card.get_absolute_url(),
            reverse('payment:card_detail', kwargs={'pk': self.card.short_pk})
        )








