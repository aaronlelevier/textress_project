from textress.settings.base import *


DEBUG = False

ALLOWED_HOSTS = ['textress.com']

SITE_URL = "textress.com"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        'NAME': os.environ['T17_DB_NAME'],                     
        'USER': os.environ['T17_DB_USER'],
        'PASSWORD': os.environ['T17_DB_PASSWORD'], 
        'HOST': '45.55.157.193',                      
        'PORT': '5432',                      
        'OPTIONS': {
            'autocommit': True,
            },
    }
}