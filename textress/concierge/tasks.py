from __future__ import absolute_import

from django.utils import timezone

from celery import shared_task
from model_mommy import mommy 

from concierge.helpers import (
    merge_twilio_messages_to_db, convert_to_json_and_publish_to_redis)
from contact.models import Contact


@shared_task
def check_twilio_messages_to_merge(guest, date=None):
    # 1. DB test simple create
    # return mommy.make(Contact)

    # 2. DB test settings.py DATABASE config
    # from django.conf import settings
    # from concierge.models import Message
    # # "autocommit" is True ?? how to turn this off?
    # print settings.DATABASES['default']['OPTIONS']
    # print Message.objects.first()

    # 3. Actual planned method
    date = date or timezone.now().date()

    for msg in merge_twilio_messages_to_db(guest=guest, date=date):
        convert_to_json_and_publish_to_redis(msg)
