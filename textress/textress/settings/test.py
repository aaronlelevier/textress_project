from .base import *


THIRD_PARTY_APPS = (
    'django_nose',
    'django_coverage',
)

INSTALLED_APPS += THIRD_PARTY_APPS


TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--nologcapture',
    '--with-coverage',
    '--cover-package=account,concierge,contact,main,payment,sms,textress,utils',
]

PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher', )

DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'