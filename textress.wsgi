import os
import sys
import site

# py2
#sys.path.append('/usr/local/lib/python2.7/dist-packages')

# py3
sys.path.append('/usr/local/lib/python3.4/dist-packages')

# project
sys.path.append('/opt/django')
sys.path.append('/opt/django/textress')
sys.path.append('/opt/django/textress/textress')


# 1st instantiate wsgi
from django.core.wsgi import get_wsgi_application
_application = get_wsgi_application()

# Add the app directories to the PYTHONPATH
os.environ['DJANGO_SETTINGS_MODULE'] = 'textress.settings.prod'


def application(environ, start_response):
    return _application(environ, start_response)