supervisord
===========

GENERAL COMMANDS
----------------
apt-get install supervisor

# start
supervisord -c /path/to/supervisord.conf

# file location:
/etc/supervisor/

# conf file location
/etc/supervisor/conf.d/

# log file location
/var/log/supervisor/


SYMLINK
-------
# symlink current dir supervisor.conf to "conf file location"
ln -s /opt/django/supervisord.conf /etc/supervisor/conf.d/ 

# stop
unlink /run/supervisor.sock
/etc/init.d/supervisor stop  # <start, stop, status, restart, etc...>


IF RESTART FAILS PROCESS
------------------------
# 1st stop supervisord
/etc/init.d/supervisor stop

# check that supervisor.sock is not connected
unlink /run/supervisor.sock

# start explicitly saying which supervisor.conf file to use
supervisord -c /path/to/supervisor.conf