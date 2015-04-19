supervisord
-----------
apt-get install supervisor

# file location:
/etc/supervisor/

# conf file location
/etc/supervisor/conf.d/

# log file location
/var/log/supervisor/

# stop
unlink /run/supervisor.sock
/etc/init.d/supervisor stop  # <start, stop, status, restart, etc...>


upstart
-------
# check `conf` file syntax
init-checkconf /etc/init/<conf_filename>.conf
