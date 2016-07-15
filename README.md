# README

This is my personal project that I worked on. It is a complete SaaS. Using this web app a
the User can send SMS and the hotel on the other end, this was meant for use with
hotels and their customers, will receive these as push notifications on the site.

### Features

What's included to make this all work, and technologies include:

- Twilio for SMS messaging, purchasing of a local phone number for the hotel, use of Twilio
Subaccounts for billing
- Stripe for payments
- Payments are structured as "pay as you go", so the customers of this SaaS refill when
out of funds. This can be done automatically if "recharge" account is turned on.
- Monthly fees for active phone numbers do occur, so this uses ``cron`` with Django custom
management commands to make that happen.
- Redis is used for the push notifications, and to keep track of recent messages in case an
account recharge is needed, instead of querying the database to see how many SMS have been sent
- Celery is used for sending of SMS and as email, so as not to affect the performance of the site. Celery uses RabbitMQ as it's message broker, and Redis as it's data store.


### If I were to iterate on this idea

The site is built using Python2 and [django-websocket-redis](https://github.com/jrief/django-websocket-redis). I would rebuild in Python3, and use [django-channels](https://github.com/andrewgodwin/channels).


### Depencencies

- redis
- rabbitmq
- supervisor
- ubuntu
- nginx
- uwsgi
- postgres


### To demo this app

1. set up virtualenv
2. pip install ``requirements_local.txt`` into virtualenv
3. run ``redis-server``
4. run ``rabbitmq-server``
5. run ``celery -A textress worker -l info``
6. install fixture data, and setup database
7. run ``./manage.py runserver``


### Other Dev Cmds

Ngrok for testing SMS public endpoint from localhost

```
cd /Applications
./ngrok http 8000
```