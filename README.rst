README
======

Dev Cmds
--------
To start all background process, in separate terminals run

.. code-block::

    ./manage.py runserver

    # nnot in use
    rabbitmq-server

    redis-server

    # nnot in use
    celery -A demo worker -l debug