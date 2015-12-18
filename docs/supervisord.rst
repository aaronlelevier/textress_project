supervisord
===========

Installation
------------
Note: ``supervisorctl <cmd>`` would't work at first, and had to reinstall through this process to get it to work.

Removal

.. code-block::

    # remove
    apt-get purge supervisor
    rm -rf /etc/supervisor
    rm -rf /var/log/supervisor

Installation

.. code-block::

    pip install meld3
    apt-get install supervisor


`Celery and Supervisor example config <https://github.com/celery/celery/blob/3.1/extra/supervisord/celeryd.conf>`_


GENERAL COMMANDS
----------------

.. code-block::

    apt-get install supervisor

    # start
    supervisord -c /path/to/supervisord.conf

    # file location:
    /etc/supervisor/

    # conf file location
    /etc/supervisor/conf.d/

    # log file location
    /var/log/supervisor/


Reload and Update

.. code-block::

    supervisorctl reread

    supervisorctl update


SYMLINK
-------

.. code-block::

    # symlink current dir supervisor.conf to "conf file location"
    ln -s /opt/django/supervisord.conf /etc/supervisor/conf.d/ 

    # stop
    unlink /run/supervisor.sock
    /etc/init.d/supervisor stop  # <start, stop, status, restart, etc...>


IF RESTART FAILS PROCESS
------------------------

.. code-block::

    # 1st stop supervisord
    sudo /etc/init.d/supervisor stop

    # check that supervisor.sock is not connected [should not have to do this step]
    unlink /run/supervisor.sock

    # start explicitly saying which supervisor.conf file to use
    supervisord -c /opt/django/supervisord.conf