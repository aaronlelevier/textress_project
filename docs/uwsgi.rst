uWSGI
=====
# test app runs
# CWD (working dir) needs to be=> /opt/django
uwsgi --socket textress.sock --wsgi-file /opt/django/textress.wsgi --chmod-socket=666

# test `ini` file
uwsgi --ini /opt/django/uwsgi.ini

STOP uWSGI
----------
uwsgi --stop /tmp/textress-master.pid

or

# find all ``uwsgi`` pids
ps ax | grep uwsgi

# stop them
killall -s INT /usr/local/bin/uwsgi



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