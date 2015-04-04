from __future__ import absolute_import

from celery import shared_task

from utils.email import Email


@shared_task
def send_email(*args, **kwargs):
    email = Email(*args, **kwargs)
    return email.msg.send()