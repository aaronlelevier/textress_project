Postgres
========

Output / Upload Database
------------------------
.. _docs: http://www.postgresql.org/docs/9.1/static/backup-dump.html

# output
pg_dump -U <username> <db_name> > outfile.sql

# upload
# [note: make sure to switch to authorized database user first.  i.e. ``su postgres``]
psql dbname < infile

# to activate `psql`
sudo su postgres

# enter postgres command line (CL)
psql

# exit postgres CL

# exit "postgres" user, and change back to root user
exit


Allow remote access
-------------------
# 1
# to be able to trust remote server, add this
# file: /etc/postgresql/9.3/main/pg_hba.conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    all             all             <server_ip>/32         md5

# 2
# what IP address(es) to listen on;
# file: /etc/postgresql/9.3/main/postgresql.conf
listen_addresses = '*'

# 3
# restart server
/etc/init.d/postgresql restart