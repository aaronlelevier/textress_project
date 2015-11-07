import datetime
import mock

from django.test import TestCase
from django.conf import settings
from django.utils import timezone

from celery import current_app
from model_mommy import mommy

from concierge.models import Guest
from concierge.tasks import archive_guests
from main.tests.factory import create_hotel
from utils import create
from utils.tests.runners import celery_set_eager


class TaskTests(TestCase):

    def setUp(self):
        self.yesterday = timezone.now().date() - datetime.timedelta(days=1)
        self.hotel = create_hotel()
        self.guest_to_archive = mommy.make(
            Guest,
            name=create._generate_name(),
            hotel=self.hotel,
            check_in=self.yesterday,
            check_out=self.yesterday,
            phone_number=create._generate_ph()
        )

    def test_archive_guest(self):
        celery_set_eager()
        self.assertEqual(Guest.objects.need_to_archive().count(), 1)
        ret = archive_guests.delay()
        self.assertEqual(Guest.objects.need_to_archive().count(), 0)