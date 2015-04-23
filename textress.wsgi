import os
import sys
import site

# Python site-packages
sys.path.append('/usr/local/lib/python2.7/dist-packages')
sys.path.append('/usr/lib/python2.7/dist-packages')
sys.path.append('/opt/django')
sys.path.append('/opt/django/textress')
sys.path.append('/opt/django/textress/textress')

# 1st instantiate wsgi
from django.core.wsgi import get_wsgi_application
_application = get_wsgi_application()

# Add the app directories to the PYTHONPATH

os.environ['DJANGO_SETTINGS_MODULE'] = 'textress.settings.prod'


def application(environ, start_response):
    os.environ['uwsgi.url_scheme'] = os.environ.get('HTTP_X_URL_SCHEME', 'http')
    return _application(environ, start_response)