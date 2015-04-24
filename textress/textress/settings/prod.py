import os

from textress.settings.base import *

os.environ['HTTPS'] = True
os.environ['wsgi.url_scheme'] = 'https'

DEBUG = True

ALLOWED_HOSTS = ['textress.com']

SITE_URL = "textress.com"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        'NAME': os.environ['T17_DB_NAME'],
        'USER': os.environ['T17_DB_USER'],
        'PASSWORD': os.environ['T17_DB_PASSWORD'], 
        'HOST': '104.131.57.229', # DB server IP.  [ was prior-> 'localhost', ]
        'PORT': '5432',
        'OPTIONS': {
            'autocommit': True,
            },
    }
}

# HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE=True