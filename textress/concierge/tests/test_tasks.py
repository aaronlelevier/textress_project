import datetime
from mock import patch

from django.test import TestCase
from django.conf import settings
from django.utils import timezone

from celery import current_app
from model_mommy import mommy

from concierge.models import Guest, Reply, Trigger, TriggerType
from concierge.tasks import archive_guests, trigger_send_message
from concierge.tests.factory import make_guests
from main.tests.factory import create_hotel
from utils import create
from utils.tests.runners import celery_set_eager


class GuestTaskTests(TestCase):

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

        celery_set_eager()

    def test_archive_guest(self):
        self.assertEqual(Guest.objects.need_to_archive().count(), 1)

        ret = archive_guests.delay()

        self.assertEqual(Guest.objects.need_to_archive().count(), 0)


class TriggerTaskTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.guest = make_guests(hotel=self.hotel, number=1)[0]
        self.reply_letter = "T"
        self.hotel_reply = mommy.make(Reply, hotel=self.hotel, letter=self.reply_letter,
            message="Thank you for staying")
        self.trigger_type = mommy.make(TriggerType, name="check_out")
        self.trigger = mommy.make(Trigger, hotel=self.hotel, type=self.trigger_type,
            reply=self.hotel_reply)

    @patch("concierge.models.Message.save")
    def test_delete_check_out_message_unit_test(self, save_mock):
        trigger_send_message(self.guest.id, 'check_out')

        self.assertTrue(save_mock.called)
