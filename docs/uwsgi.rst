uWSGI
=====
# test app runs
# CWD (working dir) needs to be=> /opt/django
uwsgi --socket textress.sock --wsgi-file /opt/django/textress.wsgi --chmod-socket=666

# test `ini` file
uwsgi -H /root/.virtualenvs/textra_17 --ini /opt/django/uwsgi.ini

STOP uWSGI
----------
uwsgi --stop /tmp/textress-master.pid

or

# find all ``uwsgi`` pids
ps ax | grep uwsgi

# stop them
killall -s INT /usr/local/bin/uwsgi



Salt
----
Remember to call: ``salt -G 'roles:appserver' state.sls uwsgi`` and not just reload
uwsgi via CL b/c ``uwsgi.ini`` uses Jinja templating and needs the IP refreshed for 
the "appserver's" IP


Emperor mode
------------
http://uwsgi-docs.readthedocs.org/en/latest/tutorials/Django_and_nginx.html#emperor-mode

# create a directory for the vassals
sudo mkdir /etc/uwsgi
sudo mkdir /etc/uwsgi/vassals
# symlink from the default config directory to your config file
sudo ln -s /path/to/your/mysite/mysite_uwsgi.ini /etc/uwsgi/vassals/
# run the emperor
uwsgi --emperor /etc/uwsgi/vassals --uid www-data --gid www-data