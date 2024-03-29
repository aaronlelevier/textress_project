from __future__ import absolute_import

from django.conf import settings
from django.utils import timezone

from celery import shared_task

from concierge.helpers import merge_twilio_messages_to_db, convert_to_json_and_publish_to_redis
from concierge.models import Guest, Reply, TriggerType, Trigger
from main.models import Hotel


@shared_task
def check_twilio_messages_to_merge(guest, date=None):
    date = date or timezone.localtime(timezone.now()).date()

    for msg in merge_twilio_messages_to_db(guest=guest, date=date):
        convert_to_json_and_publish_to_redis(msg)


@shared_task
def archive_guests():
    Guest.objects.archive()


@shared_task
def create_hotel_default_help_reply(hotel_id):
    hotel = Hotel.objects.get(id=hotel_id)
    Reply.objects.get_or_create(hotel=hotel, letter=settings.DEFAULT_REPLY_HELP_LETTER,
        message=settings.DEFAULT_REPLY_HELP_MSG, desc=settings.DEFAULT_REPLY_HELP_DESC)


@shared_task
def create_hotel_default_send_welcome(hotel_id):
    hotel = Hotel.objects.get(id=hotel_id)
    reply, _ = Reply.objects.get_or_create(hotel=hotel, letter=settings.DEFAULT_REPLY_SEND_WELCOME_LETTER,
        message=settings.DEFAULT_REPLY_SEND_WELCOME_MSG, desc=settings.DEFAULT_REPLY_SEND_WELCOME_DESC)
    trigger_type, _ = TriggerType.objects.get_or_create(name=settings.BULK_SEND_WELCOME_TRIGGER)
    Trigger.objects.get_or_create(hotel=hotel, type=trigger_type, reply=reply, active=True)


@shared_task
def trigger_send_message(guest_id, trigger_type_name):
    return Trigger.objects.send_message(guest_id, trigger_type_name)
