from django.test import TestCase

from main.tests.factory import create_hotel
from payment.forms import CardListForm
from payment.tests.factory import customer as make_customer, card as make_card


class CardListFormTests(TestCase):

    def test_add_card_default__true(self):
        """
        The "Add a card" checkbox should default to 'True' if no 'Customer'
        """
        hotel = create_hotel()
        self.assertFalse(hotel.customer)

        form = CardListForm(hotel)

        self.assertTrue(form.initial['add_card'])

    def test_add_card_default__false(self):
        """
        The "Add a card" checkbox should default to 'False' if the User has Cards.
        """
        hotel = create_hotel()
        customer = make_customer()
        card = make_card(customer.id)
        hotel.customer = customer
        hotel.save()
        self.assertTrue(hotel.customer)
        self.assertTrue(hotel.customer.cards.all())

        form = CardListForm(hotel)

        self.assertFalse(form.initial['add_card'])
