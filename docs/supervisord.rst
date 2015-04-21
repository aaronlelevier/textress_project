supervisord
===========
apt-get install supervisor

# start
supervisord -c /path/to/supervisord.conf

# file location:
/etc/supervisor/

# conf file location
/etc/supervisor/conf.d/

SYMLINK
-------
# symlink current dir supervisor.conf to "conf file location"
ln -s /opt/django/supervisord.conf /etc/supervisor/conf.d/ 

# log file location
/var/log/supervisor/

# stop
unlink /run/supervisor.sock
/etc/init.d/supervisor stop  # <start, stop, status, restart, etc...>