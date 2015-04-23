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
sudo /etc/init.d/supervisor stop

# check that supervisor.sock is not connected [should not have to do this step]
unlink /run/supervisor.sock

# start explicitly saying which supervisor.conf file to use
supervisord -c /opt/django/supervisord.conf