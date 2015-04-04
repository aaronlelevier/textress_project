import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['T17_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

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


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        'NAME': 'textra_17',                     
        'USER': os.environ['ASQL_DB_USER'],
        'PASSWORD': os.environ['ASQL_DB_PASSWORD'], 
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

SITE_URL = "localhost:8000"
SITE_NAME = 'Textress'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

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
TEXTRESS_PHONE_NUMBER = '775-419-4000'



### 3RD PARTY APPS CONFIG ###

# DJRILL
MANDRILL_API_KEY = os.environ['T17_MANDRILL_API_KEY']
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"


### TESTS ###

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=textress,contact,utils',
]

if 'test' in sys.argv:
    DEBUG = True
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'tests.db',
    }
    PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher', )
    DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'