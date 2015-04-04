from __future__ import absolute_import

from celery import shared_task

from utils.email import Email


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)


@shared_task
def hello_world():
    print('Hello World')

@shared_task
def send_email(*args, **kwargs):
    email = Email(*args, **kwargs)
    return email.msg.send()