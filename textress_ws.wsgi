import os
import sys

import gevent.socket
import redis.connection
redis.connection.socket = gevent.socket


# python 2
sys.path.append('/usr/bin/python2.7')
sys.path.append('/usr/local/lib/python2.7/dist-packages')
sys.path.append('/root/.virtualenvs/textress/lib/python2.7/site-packages')
# project
sys.path.append('/opt/django')
sys.path.append('/opt/django/textress')
sys.path.append('/opt/django/textress/textress')


os.environ['DJANGO_SETTINGS_MODULE'] = 'textress.settings.prod'

from ws4redis.uwsgi_runserver import uWSGIWebsocketServer
_application = uWSGIWebsocketServer()


def application(environ, start_response):
    return _application(environ, start_response)
