import sys
import stripe

from django.conf import settings
from django.test import TestCase

from ..models import Customer, Card, Charge


stripe.api_key = settings.STRIPE_SECRET_KEY

CUSTOMER = ""
CHARGE = ""
CARD = ""


class StripeTests(TestCase):
    
    fixtures = ['payment.json']

    def setUp(self):
        """
        TODO: Order Charge and Card by last created in Stripe, to get
            the last transaction's details.  Then set the ID of each for
            their global variables.
        """

        customer = Customer.objects.order_by('-created')[0]
        charge = customer.get_all_charges()[0] #even tho limit=1 stilll returns a list obj.
        card = charge['card']

        global CUSTOMER
        global CHARGE
        global CARD

        CUSTOMER = customer.id
        CHARGE = charge['id']
        CARD = card['id']

    def test_customer(self):
        # Customer
        customer = Customer.objects.get(id=CUSTOMER)
        assert isinstance(customer, Customer)

        # Stripe instance exists
        stripe_customer = customer.stripe_object
        assert customer.id == stripe_customer.id
        assert stripe_customer == stripe.Customer.retrieve(CUSTOMER)

    def test_card(self):
        """Make sure the Customer has a Card."""
        customer = stripe.Customer.retrieve(CUSTOMER)
        card = customer.cards.retrieve(CARD)
        assert customer
        assert card
        assert len(customer.cards.data) == 1

    def test_charges(self):
        """Should equal # of Charges coming from the Model method and
            the Stripe method."""
        customer = Customer.objects.get(id=CUSTOMER)
        charges = customer.get_all_charges()
        assert len(charges) == 1

        for charge in charges:
            stripe.Charge.retrieve(charge['id'])

        # Stripe
        assert stripe.Charge.retrieve(CHARGE)












