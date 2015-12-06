#!/bin/bash -lx

echo "Only for loading reloading database data, not a full deploy script."

echo "MUST BE AT './manage.py' DIR LEVEL!"

export DJANGO_SETTINGS_MODULE='textress.settings.prod'

source /root/.virtualenvs/textress/bin/activate

wait
./manage.py migrate

wait
echo "RELOAD SERVER SCRIPTS"

cd ../

wait
echo "UWSGI"
sudo kill -INT `cat /var/run/nginx.pid`
wait
sudo /usr/local/lib/uwsgi/uwsgi --ini uwsgi.ini
wait
ps aux | grep uwsgi

wait
echo "NGINX"
sudo cp textress.conf /etc/nginx/sites-enabled/textress.conf
wait
sudo service nginx restart
