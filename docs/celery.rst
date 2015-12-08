Celery
======

Ubuntu
------
Celery should not be run under the **root** user. Create a separate user, and put Celery in a ``virtualenv``, so it is not installed globally.


Start all process for Celery
----------------------------

.. code-block::

    # start Redis
    redis-server

    # start RabbitMQ
    rabbitmq-server

    # start Celery
    celery -A textress worker -l info


supervisord
-----------
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


Cron
----

.. code-block::

    # open "crontab" in vim
    env EDITOR=vi crontab -e

    # will run every minute
    * * * * * /path/to/task.py

    # cron mail location
    vi /var/mail/aaron


Tests
-----

.. code-block::

    # cron w/ virtualenv 
    # . $HOME/.bash_profile; # necessary for cron to access ENV VARs
    * * * * * . $HOME/.bash_profile; cd /Users/aaron/Documents/djcode/textra_project/textress && /Users/aaron/Documents/virtualenvs/django18_py2/bin/python /Users/aaron/Documents/djcode/textra_project/textress/manage.py