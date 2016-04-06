import datetime
from mock import patch

from django.test import TestCase
from django.conf import settings
from django.utils import timezone

from model_mommy import mommy

from concierge.models import Guest, Reply, Trigger, TriggerType
from concierge.tasks import (archive_guests, trigger_send_message,
    create_hotel_default_help_reply, create_hotel_default_buld_send_welcome)
from concierge.tests.factory import make_guests
from main.tests.factory import create_hotel
from utils import create
from utils.tests.runners import celery_set_eager


class GuestTaskTests(TestCase):

    def setUp(self):
        self.yesterday = timezone.localtime(timezone.now()).date() - datetime.timedelta(days=1)
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


class ReplyTaskTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.help_letter = settings.DEFAULT_REPLY_HELP_LETTER
        self.welcome_letter = settings.DEFAULT_REPLY_BULK_SEND_WELCOME_LETTER

        celery_set_eager()

    def test_create_hotel_default_help_reply(self):
        self.assertFalse(Reply.objects.filter(hotel=self.hotel, letter=self.help_letter))

        create_hotel_default_help_reply.delay(self.hotel.id)

        reply = Reply.objects.get(hotel=self.hotel, letter=self.help_letter)
        self.assertEqual(reply.hotel, self.hotel)
        self.assertEqual(reply.letter, self.help_letter)
        self.assertEqual(reply.message, settings.DEFAULT_REPLY_HELP_MSG)
        self.assertEqual(reply.desc, settings.DEFAULT_REPLY_HELP_DESC)

    def test_create_hotel_default_buld_send_welcome(self):
        self.assertFalse(Reply.objects.filter(hotel=self.hotel, letter=self.welcome_letter))
        self.assertFalse(TriggerType.objects.filter(name=settings.BULK_SEND_WELCOME_TRIGGER))
        self.assertFalse(Trigger.objects.filter(type__name=settings.BULK_SEND_WELCOME_TRIGGER,
                                                reply__letter=self.welcome_letter))

        create_hotel_default_buld_send_welcome(self.hotel.id)

        reply = Reply.objects.get(hotel=self.hotel, letter=self.welcome_letter)
        self.assertEqual(reply.hotel, self.hotel)
        self.assertEqual(reply.letter, self.welcome_letter)
        self.assertEqual(reply.message, settings.DEFAULT_REPLY_BULK_SEND_WELCOME_MSG)
        self.assertEqual(reply.desc, settings.DEFAULT_REPLY_BULK_SEND_WELCOME_DESC)
        trigger_type = TriggerType.objects.get(name=settings.BULK_SEND_WELCOME_TRIGGER)
        trigger = Trigger.objects.get(type=trigger_type, reply=reply)
        self.assertEqual(trigger.hotel, self.hotel)
        self.assertTrue(trigger.active)


class TriggerTaskTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.guest = make_guests(hotel=self.hotel, number=1)[0]

        # check-out
        self.check_out_letter = "T"
        self.check_out_message = "Thank you"
        self.check_out_trigger_name = "check_out"
        self.check_out_reply = mommy.make(Reply, hotel=self.hotel, letter=self.check_out_letter,
            message=self.check_out_message)
        self.check_out_trigger_type = mommy.make(TriggerType, name=self.check_out_trigger_name)
        self.check_out_trigger = mommy.make(Trigger, hotel=self.hotel, type=self.check_out_trigger_type,
            reply=self.check_out_reply)

        celery_set_eager()

    @patch("concierge.models.Message.save")
    def test_delete_check_out_message_unit_test(self, save_mock):
        trigger_send_message.delay(self.guest.id, self.check_out_trigger_name)

        self.assertTrue(save_mock.called)
