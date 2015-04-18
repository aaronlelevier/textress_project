from textress.settings.base import *


DEBUG = True

ALLOWED_HOSTS = [
    'textress.com',
    '104.131.57.229'
]

SITE_URL = "textress.com"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        'NAME': os.environ['T17_DB_NAME'],
        'USER': os.environ['T17_DB_USER'],
        'PASSWORD': os.environ['T17_DB_PASSWORD'], 
        'HOST': '104.131.57.229', # 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'autocommit': True,
            },
    }
}