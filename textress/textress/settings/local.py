from .base import *


THIRD_PARTY_APPS = (
    'django_extensions',
)

INSTALLED_APPS += THIRD_PARTY_APPS


SITE_URL = "http://localhost:8000"

if 'test' in sys.argv:
    from .test import *
