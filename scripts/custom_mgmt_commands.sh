#!/bin/bash

export DJANGO_SETTINGS_MODULE='textress.settings.prod'
source /home/web/.virtualenvs/textress/bin/activate

python /opt/django/textress/manage.py $1
