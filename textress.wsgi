import os
import sys
import site


# Add the app directories to the PYTHONPATH
sys.path.append('/home/django')
sys.path.append('/home/django/textress')

os.environ['DJANGO_SETTINGS_MODULE'] = 'textress.settings.prod'

import django.core.handlers.wsgi
_application = django.core.handlers.wsgi.WSGIHandler()

def application(environ, start_response):
    # DB
    os.environ['T17_DB_NAME'] = environ['T17_DB_NAME']
    os.environ['T17_DB_USER'] = environ['T17_DB_USER']
    os.environ['T17_DB_PASSWORD'] = environ['T17_DB_PASSWORD']
    # textress 
    os.environ['T17_SECRET_KEY'] = environ['TEXTRESS_SECRET_KEY']
    os.environ['T17_MANDRILL_API_KEY'] = environ['T17_MANDRILL_API_KEY']
    os.environ['T17_PHONE_NUMBER'] = environ['T17_PHONE_NUMBER']

    return _application(environ, start_response)