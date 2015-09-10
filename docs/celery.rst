Celery
======

.. code-block::

    # start Redis
    redis-server

    # start RabbitMQ
    rabbitmq-server

    # start Celery
    celery -A textress worker -l info