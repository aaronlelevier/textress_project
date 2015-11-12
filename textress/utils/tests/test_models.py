import datetime
import pytz

from django.test import TestCase
from django.conf import settings
from django.utils import timezone

from model_mommy import mommy

from account.models import Pricing
from utils.models import Dates, Tester


class DatesTests(TestCase):

    def setUp(self):
        self.tzinfo = pytz.timezone(settings.TIME_ZONE)

    def test_tzinfo(self):
        dates = Dates()
        self.assertTrue(hasattr(dates, 'tzinfo'))

    def test_all_dates(self):
        dates = Dates()
        now = timezone.now()

        self.assertTrue(dates._now)
        self.assertEqual(dates._today, now.date())
        self.assertEqual(dates._yesterday, now.date() - datetime.timedelta(days=1))
        self.assertEqual(dates._year, now.year)
        self.assertEqual(dates._month, now.month)

    def test_first_of_month(self):
        dates = Dates()
        first_of_month = dates.first_of_month(month=1, year=1)
        self.assertEqual(
            first_of_month,
            datetime.datetime(day=1, month=1,year=1, tzinfo=self.tzinfo).date()
        )

    def test_first_of_month_default(self):
        dates = Dates()
        first_of_month = dates.first_of_month()
        self.assertEqual(
            first_of_month,
            datetime.datetime(day=1, month=dates._today.month,
                year=dates._today.year, tzinfo=self.tzinfo).date()
        )

    def test_last_month_end(self):
        dates = Dates()
        self.assertEqual(
            dates.last_month_end(),
            dates.first_of_month() - datetime.timedelta(days=1)
        )


class TesterTests(TestCase):

    def test_delete(self):
        obj = mommy.make(Tester)
        self.assertFalse(obj.hidden)
        obj.delete()
        self.assertTrue(obj.hidden)

    def test_delete_override(self):
        obj = mommy.make(Tester)
        self.assertFalse(obj.hidden)
        obj.delete(override=True)
        with self.assertRaises(Tester.DoesNotExist):
            Tester.objects.get(id=obj.id)

    def test_delete_query_with_all(self):
        obj = mommy.make(Tester)
        obj.delete()
        self.assertEqual(Tester.objects.archived().count(), 1)
        self.assertEqual(Tester.objects.current().count(), 0)


class BaseModelTests(TestCase):

    def test_properties(self):
        # auto fields work
        price = mommy.make(Pricing)
        self.assertIsInstance(price.created, datetime.datetime)
        self.assertIsInstance(price.modified, datetime.datetime)
