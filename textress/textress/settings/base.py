import os
import sys

# ``textress/`` is the base dir
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


SECRET_KEY = os.environ['T17_SECRET_KEY']


DEFAULT_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    'psycopg2',
    'djrill',
    'django_nose',
    'djangular',
)

LOCAL_APPS = (
    'account',
    'contact',
)

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'textress.urls'

WSGI_APPLICATION = 'textress.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        'NAME': os.environ['T17_DB_NAME'],                     
        'USER': os.environ['T17_DB_USER'],
        'PASSWORD': os.environ['T17_DB_PASSWORD'], 
        'HOST': 'localhost',                      
        'PORT': '5432',                      
        'OPTIONS': {
            'autocommit': True,
            },
    }
}

### SITE ###

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


SITE_NAME = 'Textress'


TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
    )

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'source'),
    )

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')


### EMAIL ###
DEFAULT_FROM_EMAIL = 'sayhello@textress.com'
DEFAULT_EMAIL_SAYHELLO = 'sayhello@textress.com'
DEFAULT_EMAIL_ADMIN = 'admin@textress.com'
DEFAULT_EMAIL_SUPPORT = 'support@textress.com'
DEFAULT_EMAIL_BILLING = 'billing@textress.com'
DEFAULT_EMAIL_AARON = 'aaron@textress.com'
DEFAULT_EMAIL_NOREPLY = 'noreply@textress.com'

### OTHER CONTACT INFO ###
TEXTRESS_PHONE_NUMBER = os.environ['T17_PHONE_NUMBER'] 


### 3RD PARTY APPS CONFIG ###

# DJRILL
MANDRILL_API_KEY = os.environ['T17_MANDRILL_API_KEY']
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"


### TESTS ###

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=textress,account,contact,utils',
]

if 'test' in sys.argv:
    DEBUG = True
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'tests.db',
    }
    PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher', )
    DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'