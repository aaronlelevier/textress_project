uWSGI
=====

INSTALLATION
-----
.. code-block::

    # python 3 req
    sudo apt-get install libpcre3 libpcre3-dev

    # in virtualenv
    pip uninstall uwsgi
    sudo apt-get remove uwsgi

    # download and unwrap
    wget http://projects.unbit.it/downloads/uwsgi-2.0.3.tar.gz
    tar -xvf uwsgi-2.0.3.tar.gz
    cd uwsgi-2.0.3

    # build
    python uwsgiconfig.py --build

    # start
    /usr/local/lib/uwsgi/uwsgi --ini uwsgi.ini


TEST RUN

.. code-block::

    # test app runs
    # CWD (working dir) needs to be=> /opt/django
    uwsgi --socket textress.sock --wsgi-file /opt/django/textress.wsgi --chmod-socket=666

TEST

.. code-block::

    uwsgi --socket :9000 -H /root/.virtualenvs/textra_17 --no-site --wsgi-file /opt/django/test.py


START

.. code-block::

    uwsgi --ini /opt/django/uwsgi.ini


Basict Test

.. code-block::

    # link on setup
    http://uwsgi-docs.readthedocs.org/en/latest/tutorials/Django_and_nginx.html#basic-test

Run

.. code-block::

    uwsgi --http :9000 --wsgi-file test.py


STOP uWSGI

.. code-block::

    uwsgi --stop /tmp/textress-master.pid

    # OR

    # find all ``uwsgi`` pids
    ps ax | grep uwsgi

    # stop them
    killall -s INT uwsgi



Salt
----
Remember to call: ``salt -G 'roles:appserver' state.sls uwsgi`` and not just reload
uwsgi via CL b/c ``uwsgi.ini`` uses Jinja templating and needs the IP refreshed for 
the "appserver's" IP


Emperor mode
------------
http://uwsgi-docs.readthedocs.org/en/latest/tutorials/Django_and_nginx.html#emperor-mode

.. code-block::


    # create a directory for the vassals
    sudo mkdir /etc/uwsgi
    sudo mkdir /etc/uwsgi/vassals
    # symlink from the default config directory to your config file
    sudo ln -s /path/to/your/mysite/mysite_uwsgi.ini /etc/uwsgi/vassals/
    # run the emperor
    uwsgi --emperor /etc/uwsgi/vassals --uid www-data --gid www-data