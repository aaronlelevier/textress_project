nginx
=====

.. code-block::

    # make unix websocket executable
    chomod 0666 textress.sock

    # test `conf` files
    nginx -t

    # START
    sudo /etc/init.d/nginx start 


RESTART
-------

.. code-block::

    # collectstatic ??
    python /opt/django/textress/manage.py collectstatic

    sudo /etc/init.d/nginx restart



MISC
----

.. code-block::

    # remove default
    rm /etc/init/sites-enabled/default

    # add textress.conf to sites enabled
    ln -s /opt/django/textress.conf /etc/nginx/sites-enabled/textress.conf


nginx + uwsgi proxy test
------------------------

.. code-block::

    # port 9000 is forwarding to port 80

    http://uwsgi-docs.readthedocs.org/en/latest/tutorials/Django_and_nginx.html#nginx-and-uwsgi-and-test-py

    upstream django {
        server my.i.p.addr:9000 fail_timeout=0; 
    }
    server {
        listen 80;
        server_name example.com;

        location / {
            # uWSGI config
            uwsgi_pass textress; # name of the `upstream` server
            include /opt/django/uwsgi_params; # the uwsgi_params file you installed
        }
    }

    # reload nginx and run w/ uwsgi
    sudo /etc/init.d/nginx restart
    uwsgi --socket :9000 --wsgi-file test.py


SSL
---
Go to the "Renew Certificate" section in NameCheap, and follow the below steps to generate the initial CSR.

.. code-block::

    https://www.digitalocean.com/community/tutorials/how-to-create-an-ssl-certificate-on-nginx-for-ubuntu-14-04

    # cert location
    /etc/nginx/ssl/

    # key
    openssl genrsa -out /etc/nginx/ssl/textress.com.key 2048

    # csr
    openssl req -new -sha256 -key /etc/nginx/ssl/textress.com.key -out /etc/nginx/ssl/textress.com.csr

Call Namecheap for ``bundle.crt``

Concat to create ``chained.crt``

`resource <http://nginx.org/en/docs/http/configuring_https_servers.html>`_

.. code-block::

    cat www.example.com.crt bundle.crt > www.example.com.chained.crt
