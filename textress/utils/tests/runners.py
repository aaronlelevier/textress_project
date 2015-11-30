from django.conf import settings

from celery import current_app


def celery_set_eager():
    settings.CELERY_ALWAYS_EAGER = True
    current_app.conf.CELERY_ALWAYS_EAGER = True
    settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
    current_app.conf.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True