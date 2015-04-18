Postgres
--------

# to activate `psql`
sudo su postgres
psql

# to change back to root user
exit


Allow remote access
-------------------
# 1
# to be able to trust remote server, add this
# file: /etc/postgresql/9.3/main/pg_hba.conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    all             all             45.55.182.26/32         md5
host    all             all             104.131.57.229/32       md5

# 2
# what IP address(es) to listen on;
# file: /etc/postgresql/9.3/main/postgresql.conf
listen_addresses = '*'

# 3
# restart server
/etc/init.d/postgresql restart