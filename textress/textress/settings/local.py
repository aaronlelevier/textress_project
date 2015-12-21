from .base import *


SITE_URL = "http://localhost:8000"

THIRD_PARTY_APPS = (
    'django_extensions',
)

INSTALLED_APPS += THIRD_PARTY_APPS


### DJANGO DEBUG TOOLBAR ###
INSTALLED_APPS += ('debug_toolbar',)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INTERNAL_IPS = ('127.0.0.1',)


if 'test' in sys.argv:
    from .test import *
