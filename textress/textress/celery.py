from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'textress.settings')

app = Celery('textress', backend='redis://localhost', broker='amqp://')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.task(bind=True)
def db_test_query(self):
    from django.conf import settings
    print "Settings w/i Task:", settings.DATABASES['default']['OPTIONS']

    from account.models import Pricing
    return Pricing.objects.all()
