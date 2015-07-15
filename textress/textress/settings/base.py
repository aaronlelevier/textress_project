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
    'django_nose',
    'rest_framework',
    'rest_framework.authtoken',
    'djangular',
    'django_coverage',
    'ws4redis',
    'django_extensions',
)

LOCAL_APPS = (
    'main',
    'contact',
    'sms',
    'concierge',
    'account',
    'payment',
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
        'OPTIONS': {},
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


SITE =  "textress.com"
SITE_NAME = 'Textress'
SITE_URL = "localhost:8000/"


### STATIC ACCOUNT URLS ###
LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL = '/account/private/'
LOGIN_ERROR_URL = '/account/login-error/'
VERIFY_LOGOUT_URL = '/account/verify-logout/'
REDIRECT_FIELD_NAME = '/'
LOGIN_REDIRECT = '/account/conversation/'
LOGIN_SUCCESS_URL = '/account/'


### EMAIL ###
DEFAULT_FROM_EMAIL = 'sayhello@textress.com'
DEFAULT_TO_EMAIL = DEFAULT_FROM_EMAIL
DEFAULT_EMAIL_SAYHELLO = 'sayhello@textress.com'
DEFAULT_EMAIL_ADMIN = 'admin@textress.com'
DEFAULT_EMAIL_SUPPORT = 'support@textress.com'
DEFAULT_EMAIL_BILLING = 'billing@textress.com'
DEFAULT_EMAIL_AARON = 'aaron@textress.com'
DEFAULT_EMAIL_NOREPLY = 'noreply@textress.com'

### OTHER CONTACT INFO ###
TEXTRESS_PHONE_NUMBER = os.environ['T17_PHONE_NUMBER']
TEXTRESS_HOTEL = 'Aaron Test'

COMPANY_NAME = "Textress"

# Textress Concierge Settings
SMS_LIMIT = 50
# Default Costs for Accounts (Stripe Amounts ~ in cents)
DEFAULT_MONTHLY_FEE = 0
DEFAULT_SMS_COST = 5.5
PHONE_NUMBER_CHARGE = 300
PHONE_NUMBER_MONTHLY_COST = 100

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
    # 'DEFAULT_PERMISSION_CLASSES': (
    #     'rest_framework.permissions.IsAuthenticated',
    # ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'PAGINATE_BY': 10
}

# JWT_AUTH = {
#     'JWT_EXPIRATION_DELTA': datetime.timedelta(days=14),
#     'JWT_ALLOW_REFRESH': True,
#     'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=14)
# }

# CELERY
# BROKER_URL = 'redis://127.0.0.1:6379/0'
# BROKER_TRANSPORT = 'redis'
# CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

# TWILIO
PHONE_NUMBER = os.environ['TWILIO_PHONE_NUMBER']
TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']

if DEBUG:
    # STRIPE
    STRIPE_SECRET_KEY = os.environ['STRIPE_TEST_SECRET_KEY']
    STRIPE_PUBLIC_KEY = os.environ['STRIPE_TEST_PUBLIC_KEY']
else:
    # STRIPE
    STRIPE_SECRET_KEY = os.environ['STRIPE_LIVE_SECRET_KEY']
    STRIPE_PUBLIC_KEY = os.environ['STRIPE_LIVE_PUBLIC_KEY']

TWILIO_RESOURCE_URI = "www.twilio.com/2010-01-01/Accounts/"+TWILIO_ACCOUNT_SID


### REDIS ###

SESSION_ENGINE = 'redis_sessions.session'

SESSION_REDIS_PREFIX = 'session'


### DJANGO-WEBSOCKET-REDIS ###

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

LOGGING = None
#  {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'simple': {
#             'format': '[%(asctime)s %(module)s] %(levelname)s: %(message)s'
#         },
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }
