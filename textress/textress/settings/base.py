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
)

THIRD_PARTY_APPS = (
    'psycopg2',
    'django_nose',
    'rest_framework',
    'rest_framework.authtoken',
    'djangular',
    'django_coverage',
)

LOCAL_APPS = (
    'main',
    'contact',
    'sms',
    'concierge',
    'account',
    'payment',
)

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS


AUTHENTICATION_BACKENDS = (
    # Defaulth Auth backend for Users registered via Django
    'django.contrib.auth.backends.ModelBackend',
)


### [TODO: will this be replaced by Redis ??]
# For Cache templates and inc 
# TEMPLATE_LOADERS = (
#     ('django.template.loaders.cached.Loader', (
#         'django.template.loaders.filesystem.Loader',
#         'django.template.loaders.app_directories.Loader',
#     )),
# )

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.static',
    )


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


SITE =  "textress.com"
SITE_NAME = 'Textress'
SITE_URL = "localhost:8000/"

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
    )

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'source'),
    )

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')


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
DEFAULT_EMAIL_SAYHELLO = 'sayhello@textress.com'
DEFAULT_EMAIL_ADMIN = 'admin@textress.com'
DEFAULT_EMAIL_SUPPORT = 'support@textress.com'
DEFAULT_EMAIL_BILLING = 'billing@textress.com'
DEFAULT_EMAIL_AARON = 'aaron@textress.com'
DEFAULT_EMAIL_NOREPLY = 'noreply@textress.com'

### OTHER CONTACT INFO ###
TEXTRESS_PHONE_NUMBER = os.environ['T17_PHONE_NUMBER']

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

# Celery
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

### TESTS ###

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=textress,account,contact,payment,sms,utils',
]

if 'test' in sys.argv:
    DEBUG = True
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'tests.db',
    }
    PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher', )
    DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'