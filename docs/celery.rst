Celery
======

.. code-block::

    # start Redis
    redis-server

    # start RabbitMQ
    rabbitmq-server

    # start Celery
    celery -A textress worker -l info


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