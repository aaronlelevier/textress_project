from textress.settings.base import *


DEBUG = True

ALLOWED_HOSTS = ['*']

if 'test' in sys.argv:
    from .test import *