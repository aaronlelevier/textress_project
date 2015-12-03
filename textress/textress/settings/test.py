from .base import *


THIRD_PARTY_APPS = (
    'django_nose',
    'django_coverage',
    'django_extensions',
)

INSTALLED_APPS = set(INSTALLED_APPS + THIRD_PARTY_APPS)


TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--nologcapture',
    '--with-coverage',
    '--cover-package=account,concierge,contact,main,payment,sms,textress,utils',
]

LOGGING = None
DEBUG = True
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': 'tests.db',
}
PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher', )
DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'