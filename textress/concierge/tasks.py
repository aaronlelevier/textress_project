from __future__ import absolute_import

from django.utils import timezone

from celery import shared_task

from concierge.helpers import (
    merge_twilio_messages_to_db, convert_to_json_and_publish_to_redis)


@shared_task
def check_twilio_messages_to_merge(guest):
    from django.conf import settings
    from concierge.models import Message

    # "autocommit" is True ?? how to turn this off?
    print settings.DATABASES['default']['OPTIONS']
    print Message.objects.first()
    # for msg in merge_twilio_messages_to_db(guest=guest, date=timezone.now().date()):
    #     # these SMS then need to be published to Redis for the Hotel or 
    #     # Guest, and appear on the right side of Send/Receive in the GuestDetailView
    #     convert_to_json_and_publish_to_redis(msg)
