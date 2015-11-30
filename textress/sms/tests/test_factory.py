from django.test import TestCase

from main.tests.factory import create_hotel
from sms.models import PhoneNumber
from sms.tests import factory


class FactoryTests(TestCase):

    def test_create_phone_number(self):
        ph_num = factory.create_phone_number()
        self.assertIsInstance(ph_num, PhoneNumber)

    def test_create_two_phone_numbers(self):
        factory.create_phone_number()
        factory.create_phone_number()
        self.assertEqual(PhoneNumber.objects.count(), 2)

    def test_hotel(self):
        hotel = create_hotel()
        ph1 = factory.create_phone_number(hotel)
        ph2 = factory.create_phone_number(hotel)
        self.assertEqual(PhoneNumber.objects.filter(hotel=hotel).count(), 2)
