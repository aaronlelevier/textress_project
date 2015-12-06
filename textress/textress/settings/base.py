import os
import sys

DEBUG = True

ALLOWED_HOSTS = ['*']

SITE_ID = 1

# ``../textra_project/textress/`` is the base dir
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

SECRET_KEY = os.environ['T17_SECRET_KEY']

DEFAULT_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.flatpages',
    'django.contrib.postgres',
)

THIRD_PARTY_APPS = (
    'psycopg2',
    'rest_framework',
    'rest_framework.authtoken',
    'djangular',
    'ws4redis',
)

LOCAL_APPS = (
    'account',
    'concierge',
    'contact',
    'main',
    'payment',
    'sms',
    'utils',
)

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS


AUTHENTICATION_BACKENDS = (
    # Defaulth Auth backend for Users registered via Django
    'django.contrib.auth.backends.ModelBackend',
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'textress.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.core.context_processors.static',
                'django.core.context_processors.media',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ws4redis.context_processors.default',
            ],
        },
    },
]

WSGI_APPLICATION = 'textress.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        'NAME': os.environ['T17_DB_NAME'],
        'USER': os.environ['T17_DB_USER'],
        'PASSWORD': os.environ['T17_DB_PASSWORD'],
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

### SITE ###

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


ADMIN_MEDIA_PREFIX = '/admin-media/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'source'),
    # os.path.join(BASE_DIR, 'media'),
    )

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
    },
}


SITE =  "textress.com"
SITE_NAME = 'Textress'
SITE_URL = "https://textress.com"


### STATIC ACCOUNT URLS ###
LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL = '/account/private/'
LOGIN_ERROR_URL = '/account/login-error/'
VERIFY_LOGOUT_URL = '/account/verify-logout/'
REDIRECT_FIELD_NAME = '/'
LOGIN_REDIRECT = '/account/conversation/'
LOGIN_SUCCESS_URL = '/account/'


### EMAIL ###

# django native settings for ``django.core.mail.mail_admins()``
EMAIL_HOST_USER = 'admin@textress.com'
EMAIL_HOST_PASSWORD = os.environ['TEXTRESS_EMAIL_PASSWORD']

# other emails
DEFAULT_FROM_EMAIL = 'sayhello@textress.com'
DEFAULT_TO_EMAIL = DEFAULT_FROM_EMAIL
DEFAULT_EMAIL_SAYHELLO = 'sayhello@textress.com'
DEFAULT_EMAIL_ADMIN = 'admin@textress.com'
DEFAULT_EMAIL_SUPPORT = 'support@textress.com'
DEFAULT_EMAIL_BILLING = 'billing@textress.com'
DEFAULT_EMAIL_AARON = 'aaron@textress.com'
DEFAULT_EMAIL_NOREPLY = 'noreply@textress.com'

SUPERUSER_USERNAME = 'aaron'
SUPERUSER_EMAIL = 'aaron@textress.com'
SUPERUSER_PASSWORD = os.environ['T17_DB_PASSWORD']

### OTHER CONTACT INFO ###
TEXTRESS_PHONE_NUMBER = os.environ['T17_PHONE_NUMBER']

COMPANY_NAME = "Textress"

# At this "Limit", post an AcctTran 'sms_used' to check if account
# needs to be recharged.
CHECK_SMS_LIMIT = 100

# Default Costs for Accounts (Stripe Amounts ~ in cents)
DEFAULT_MONTHLY_FEE = 0
DEFAULT_SMS_COST = 5.00
PHONE_NUMBER_CHARGE = 300
PHONE_NUMBER_MONTHLY_COST = 300
PHONE_NUMBER_MONTHLY_CHARGE_DAY = 1 # 1st of the month

### Twilio Settings ###
DEFAULT_TO_PH = "+17754194000"
DEFAULT_TO_PH_2 = "+17023012823"
DEFAULT_TO_PH_BAD = "+14043488557"

DEFAULT_FROM_PH = os.environ['TWILIO_PHONE_NUMBER'] # +17024302691
DEFAULT_FROM_PH_BAD = "+1234567890"

RESERVED_REPLY_LETTERS = ['Y', 'S'] # 'H' for HELP will be added to each Hotel upon signup


### 3RD PARTY APPS CONFIG ###

# DJRILL
MANDRILL_API_KEY = os.environ['T17_MANDRILL_API_KEY']
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"

# DJANGO-REST-FRAMEWORK
REST_FRAMEWORK = {
    'PAGINATE_BY': 100,
    'MAX_PAGINATE_BY': 100,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
}


### TWILIO

# master
PHONE_NUMBER = os.environ['TWILIO_PHONE_NUMBER']
TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
# aaron hotel
PHONE_NUMBER_TEST = os.environ['TWILIO_PHONE_NUMBER_TEST']
TWILIO_ACCOUNT_SID_TEST = os.environ['TWILIO_ACCOUNT_SID_TEST']
TWILIO_AUTH_TOKEN_TEST = os.environ['TWILIO_AUTH_TOKEN_TEST']

TWILIO_RESOURCE_URI = "www.twilio.com/2010-01-01/Accounts/"+TWILIO_ACCOUNT_SID


### STRIPE

STRIPE_SECRET_KEY = os.environ['STRIPE_TEST_SECRET_KEY']
STRIPE_PUBLIC_KEY = os.environ['STRIPE_TEST_PUBLIC_KEY']


### REDIS

SESSION_ENGINE = 'redis_sessions.session'

SESSION_REDIS_PREFIX = 'session'


### DJANGO-WEBSOCKET-REDIS

WEBSOCKET_URL = '/ws/'

# This setting is required to override the Django's main loop, when running in
# development mode, such as ./manage runserver
WSGI_APPLICATION = 'ws4redis.django_runserver.application'

# URL that distinguishes websocket connections from normal requests
WEBSOCKET_URL = '/ws/'

# Set the number of seconds each message shall persited
WS4REDIS_EXPIRE = 3600

WS4REDIS_HEARTBEAT = '--heartbeat--'

WS4REDIS_PREFIX = 'demo'


### LOGGING ###

LOGGING_DIR = os.path.join(os.path.dirname(BASE_DIR), "log") # ../textra_project/log/

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGGING_DIR, 'debug.log'),
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'textress': {
            'handlers': ['file'],
            'level': 'DEBUG'
        }
    }
}

import logging, copy
from django.utils.log import DEFAULT_LOGGING

LOGGING = copy.deepcopy(DEFAULT_LOGGING)
LOGGING['filters']['suppress_deprecated'] = {
    '()': 'textress.settings.SuppressDeprecated'  
}
LOGGING['handlers']['console']['filters'].append('suppress_deprecated')

class SuppressDeprecated(logging.Filter):
    def filter(self, record):
        WARNINGS_TO_SUPPRESS = [
            'RemovedInDjango19Warning'
        ]
        # Return false to suppress message.
        return not any([warn in record.getMessage() for warn in WARNINGS_TO_SUPPRESS])
