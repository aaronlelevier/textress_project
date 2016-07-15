Redis
=====

`Redis Quickstart <http://redis.io/topics/quickstart>`_

.. code-block::

    # start from CL w/ Mac
    redis-server


Ubuntu
------

Installation

```
cd ~
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make

apt-get install redis-server
```

To test

```
redis-cli ping
```