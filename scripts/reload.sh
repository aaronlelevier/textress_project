#!/bin/bash -lx

echo "Only for loading reloading database data, not a full deploy script."
echo "MUST BE AT './manage.py' DIR LEVEL!"

export DJANGO_SETTINGS_MODULE='textress.settings.prod'

source /root/.virtualenvs/textress/bin/activate

wait
echo "CREATE STATIC ASSETS DIRS"
if [ ! -d "/var/www/static" ]; then mkdir -p /var/www/static; fi
if [ ! -d "/var/www/media" ]; then mkdir -p /var/www/media; fi

wait
echo "COPY STATIC ASSETS"
./manage.py collectstatic --noinput

wait
echo "COPY MEDIA ASSETS"
cp -R media/ /var/www/

wait
./manage.py migrate

wait
echo "RELOAD SERVER SCRIPTS"

cd ../

wait
echo "uWSGI"
sudo killall -s INT uwsgi
wait
sudo /usr/local/lib/uwsgi/uwsgi --ini uwsgi.ini

wait
echo "NGINX"
sudo cp textress.conf /etc/nginx/sites-enabled/textress.conf
wait
sudo service nginx restart

echo "Check uWSGI process count"
wait
sleep 5s
ps aux | grep uwsgi
