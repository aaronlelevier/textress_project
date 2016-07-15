Celery
======

Ubuntu
------
Celery should not be run under the **root** user. Create a separate user, and put Celery in a ``virtualenv``, so it is not installed globally.

Common Commands
---------------
.. code-block::

    celery inspect active

    celery inspect scheduled

    # this is the command that will show the same as run w/ "log info" in dev.
    celery inspect registered


Start all process for Celery
----------------------------

.. code-block::

    # start Redis
    redis-server

    # start RabbitMQ
    rabbitmq-server

    # start Celery
    celery -A textress worker -l info


For a Queue
-----------

Command Line

.. code-block::

    celery -A textress worker -l info -Q <queue_name>
    
In the Python code

.. code-block::

    my_task.apply_async(queue=<queue_name>)


Cron
----

`Blog about Cron <http://kvz.io/blog/2007/07/29/schedule-tasks-on-linux-using-crontab/>`_

.. code-block::

    # open "crontab" in vim
    env EDITOR=vi crontab -e

    # will run every minute
    * * * * * /path/to/task.py

    # cron mail location
    vi /var/mail/aaron

Log Location

.. code-block::

    /var/log/syslog

    grep CRON /var/log/syslog


Tests
-----

.. code-block::

    # cron w/ virtualenv 
    # . $HOME/.bash_profile; # necessary for cron to access ENV VARs
    * * * * * . $HOME/.bash_profile; cd /Users/aaron/Documents/djcode/textra_project/textress && /Users/aaron/Documents/virtualenvs/django18_py2/bin/python /Users/aaron/Documents/djcode/textra_project/textress/manage.py
