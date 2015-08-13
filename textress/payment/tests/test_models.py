import stripe

from django.conf import settings
from django.test import TestCase
from django.core.exceptions import ValidationError

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


### CARD

class CardManagerTests(TestCase):

    def setUp(self):
        # 2 Customers w/ 2 Cards each.
        self.customer = factory.customer()
        self.card = factory.card(customer_id=self.customer.id)
        # Other Customer/Card
        self.customer2 = factory.customer()
        self.card2 = factory.card(customer_id=self.customer2.id)

    def test_create(self):
        self.assertEqual(Customer.objects.count(), 2)
        self.assertEqual(Card.objects.count(), 2)

    def test_validate_card(self):
        # If Card is returned, (no Error Raised) the card is Valid
        self.assertTrue(Card.objects._validate_card(self.customer, self.card.id))

    def test_validate_card_validationerror(self):
        with self.assertRaises(ValidationError):
            Card.objects._validate_card(self.customer, 'bad-card-id')

    def test_set_default(self):
        # Set False
        self.card.default = False
        self.card.save()
        self.assertFalse(self.card.default)
        # Set True
        card = Card.objects._set_default(self.customer, self.card.id)
        self.assertTrue(card.default)

    def test_update_non_defaults(self):
        # Default
        card = Card.objects._set_default(self.customer, self.card.id)
        # Non-Defaults
        Card.objects._update_non_defaults(self.customer, self.card.id)
        self.assertTrue(card.default)
        self.assertEqual(Card.objects.filter(customer=self.customer, default=True).count(), 1)

    def test_update_default(self):
        Card.objects.update_default(self.customer, self.card.id)
        self.assertEqual(Card.objects.filter(customer=self.customer, default=True).count(), 1)

    def test_delete_card(self):
        Card.objects.delete_card(self.customer, self.card.id)
        with self.assertRaises(Card.DoesNotExist):
            Card.objects.get(id=self.card.id)


class CardTests(TestCase):

    def setUp(self):
        self.customer = factory.customer()
        self.card = factory.card(customer_id=self.customer.id)

    ### Save Logic

    def test_default(self):
        self.assertTrue(self.card.default)

    def test_stripe_object_attr(self):
        self.assertTrue(hasattr(self.card, 'stripe_object'))

    def test_expires(self):
        self.assertIsInstance(self.card.expires, str)

    def test_image(self):
        self.assertTrue(self.card.image)


class ChargeTests(TestCase):

    def setUp(self):
        self.charge = factory.charge()

    def test_stripe_object_attr(self):
        self.assertTrue(hasattr(self.charge, 'stripe_object'))




