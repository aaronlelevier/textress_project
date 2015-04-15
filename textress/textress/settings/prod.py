from textress.settings.base import *


DEBUG = False

ALLOWED_HOSTS = ['textress.com']

SITE_URL = "textress.com"

SECRET_KEY = '{{ pillar["T17_SECRET_KEY"] }}'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        'NAME': '{{ pillar["T17_DB_NAME"] }}',                     
        'USER': '{{ pillar["T17_DB_USER"] }}',
        'PASSWORD': '{{ pillar["T17_DB_PASSWORD"] }}', 
        'HOST': '{{ pillar["MINION_IP"] }}',                      
        'PORT': '5432',                      
        'OPTIONS': {
            'autocommit': True,
            },
    }
}

TEXTRESS_PHONE_NUMBER = '{{ pillar["T17_PHONE_NUMBER"] }}' 

MANDRILL_API_KEY = '{{ pillar["T17_MANDRILL_API_KEY"] }}'