import os
import sys


# python 2
sys.path.append('/usr/bin/python2.7')
sys.path.append('/usr/local/lib/python2.7/dist-packages')
sys.path.append('/root/.virtualenvs/textress/lib/python2.7/site-packages')

# project
sys.path.append('/opt/django')
sys.path.append('/opt/django/textress')
sys.path.append('/opt/django/textress/textress')

# Add the app directories to the PYTHONPATH
os.environ['DJANGO_SETTINGS_MODULE'] = 'textress.settings.prod'

# 1st instantiate wsgi
from django.core.wsgi import get_wsgi_application
_application = get_wsgi_application()

def application(environ, start_response):
    return _application(environ, start_response)