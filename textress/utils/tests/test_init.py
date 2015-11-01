from django.core.exceptions import ValidationError
from django.test import TestCase

from utils import validate_phone, ph_formatter


class UtilInitTests(TestCase):

    def setUp(self):
        self.init_phone = "7025101234"

    def test_validate_phone(self):
        ph = validate_phone(self.init_phone)
        self.assertEqual(ph, "+1"+self.init_phone)

    def test_validate_phone_raise(self):
        with self.assertRaises(ValidationError):
            validate_phone("this isn't a phone number")

    def test_ph_formatter(self):
        phone = validate_phone(self.init_phone) 
        formatted_phone = ph_formatter(self.init_phone)
        self.assertEqual(
            formatted_phone,
            "({}) {}-{}".format(phone[2:5], phone[5:8], phone[8:])
        )
