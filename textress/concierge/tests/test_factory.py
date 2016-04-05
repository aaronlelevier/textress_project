from django.test import TestCase

from concierge.models import Guest, Message, Hotel
from concierge.tests import factory
from main.tests.factory import create_hotel, create_hotel_user


class FactoryTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel)

    def test_make_guests(self):
        self.assertEqual(Guest.objects.count(), 0)
        factory.make_guests(self.hotel)
        self.assertEqual(Guest.objects.filter(hotel=self.hotel).count(), 10)

    def test_make_single_guest(self):
        guest = factory.make_guests(self.hotel, number=1)[0]
        self.assertIsInstance(guest, Guest)

    def test_make_messages(self):
        guest = factory.make_guests(self.hotel, number=1)[0]
        self.assertEqual(Message.objects.count(), 0)
        messages = factory.make_messages(
            hotel=self.hotel,
            user=self.user,
            guest=guest
        )
        self.assertEqual(Message.objects.filter(hotel=self.hotel).count(), 10)

    # TODO: missing test coverage for `make_messages`
