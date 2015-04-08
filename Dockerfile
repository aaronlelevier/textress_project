FROM ubuntu:trusty
MAINTAINER Aaron Lelevier <pyaaron@gmail.com>

# FROM python:3.4
# FROM postgres
# FROM redis
# FROM rabbitmq

RUN apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential git python python-dev python-setuptools nginx supervisor postgresql-server-dev-9.3 libpq-dev
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y postgresql postgresql-contrib

RUN easy_install pip
RUN pip install uwsgi

ADD . /opt/django/

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/sites-enabled/default
RUN ln -s /opt/django/django.conf /etc/nginx/sites-enabled/
RUN ln -s /opt/django/supervisord.conf /etc/supervisor/conf.d/

# pip install and prerequisites
RUN DEBIAN_FRONTEND=noninteractive apt-get install libncurses5-dev
RUN pip install gnureadline==6.3.3
RUN pip install -r /opt/django/requirements.txt