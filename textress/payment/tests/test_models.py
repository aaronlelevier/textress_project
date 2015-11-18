import stripe

from django.conf import settings
from django.test import TestCase
from django.core.exceptions import ValidationError

from main.models import Subaccount
from main.tests.factory import create_hotel, create_hotel_user, make_subaccount
from payment.models import StripeClient, Customer, Card, Charge, Refund
from payment.tests import factory
from utils import create

# Set Stripe Key for All tests
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeClientTests(TestCase):

    def test_init(self):
        sc = StripeClient()
        self.assertIsInstance(sc, StripeClient)
        self.assertTrue(hasattr(sc, 'stripe'))
        self.assertIsNotNone(sc.stripe.api_key)


class PmtBaseModelTests(TestCase):

    def test_short_pk(self):
        self.customer = factory.customer()
        self.assertEqual(self.customer.short_pk, self.customer.id[-10:])


class CustomerTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel, group='hotel_admin')
        self.customer = factory.customer()

    def test_stripe_create__raise_error(self):
        with self.assertRaises(stripe.error.StripeError):
            Customer.objects.stripe_create(hotel=self.hotel, token='foo',
                email=self.user.email)

    def test_stripe_attr(self):
        self.assertTrue(hasattr(self.customer, 'stripe'))

    def test_stripe_object(self):
        self.assertIsInstance(
            self.customer.stripe_object,
            stripe.resource.Customer
        )

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
        self.assertIsInstance(
            self.customer.stripe_object,
            stripe.resource.Customer
        )

    def test_expires(self):
        self.assertIsInstance(self.card.expires, str)

    def test_image(self):
        self.assertTrue(self.card.image)


class ChargeManagerTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.subaccount = make_subaccount(self.hotel)
        self.customer = factory.customer()
        self.card = factory.card(self.customer.id)
        self.hotel.update_customer(self.customer)

    def test_stripe_create(self):
        amount = 1000
        init_charges = stripe.Charge.all(customer=self.customer, limit=100)
        charge = Charge.objects.stripe_create(self.hotel, amount)
        post_charges = stripe.Charge.all(customer=self.customer, limit=100)

        # Stripe charge posted
        self.assertIsInstance(
            stripe.Charge.retrieve(charge.id),
            stripe.resource.Charge
        )

        # Subaccount now exists
        self.assertIsInstance(self.hotel.subaccount, Subaccount)

        # DB record created
        self.assertIsInstance(charge, Charge)
        self.assertEqual(charge.card, self.card)
        self.assertEqual(charge.customer, self.customer)


class ChargeTests(TestCase):

    def setUp(self):
        self.charge = factory.charge()

    def test_stripe_object_attr(self):
        self.assertIsInstance(
            self.charge.stripe_object,
            stripe.resource.Charge
        )