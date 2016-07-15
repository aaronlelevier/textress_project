# Server Setup Notes

### apt-get

```
git

nginx

python-pip
```

### virtualenv

m```
cd /
mkdir ./virtualenv
virtualenv -p /usr/bin/python3.4 <virtualenv_name>
```

### pip packages

Need python-dev, or else will get error: *<Python.h> no such file or directory**, so install:

```
# python 2
apt-get install python-dev

apt-get install python3-dev
```


### Pillow

This is required for using Django's ImageField.

``apt-get install python3-dev`` is a pre-requisite to installing Pillow.

```
apt-get apt-get install libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev

pip instal pillow
```


### git clone repo

use ssh clone type
need to add Deployment Key (read-only ssh key) to repo first

[Link](https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/)


### repo location

```
mkdir opt
cd opt
git clone <ssh remote repo name> django
```


### PostgreSQL

##### Install

```
sudo apt-get install postgresql-9.3 postgresql-contrib postgresql-client postgresql-server-dev-9.3
```

##### In order to login to psql

/etc/postgresql/9.3/main/postgresql.conf
listen_addresses = '*'

/etc/postgresql/9.3/main/pg_hba.conf
local   all         postgres                          md5

# rn on command line
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"


##### If PG Cluster doesn't exist:
Will create new ``/etc/postgres/...`` files

pg_createcluster 9.3 foo
pg_createcluster <version> <name>

##### Remove
apt-get remove ... will remove packages only
apt-get purge ... will remove packages and config files

