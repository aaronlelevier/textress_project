import datetime

from django.test import TestCase
from django.utils import timezone

from concierge.forms import GuestForm


class GuestFormTests(TestCase):

    def setUp(self):
        self.form = GuestForm()

    def test_initial__phone_number(self):
        self.assertEqual(self.form.initial['phone_number'], '')

    def test_initial__check_in(self):
        self.assertEqual(self.form.initial['check_in'], timezone.localtime(timezone.now()).date())

    def test_initial__check_out(self):
        self.assertEqual(
            self.form.initial['check_out'],
            timezone.localtime(timezone.now()).date()+datetime.timedelta(days=1)
        )
