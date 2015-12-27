#!/bin/bash -lx

echo "Reload GIT changes on live server script"
echo "MUST BE AT './manage.py' DIR LEVEL!"

git pull
wait

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
echo "uWSGI for main Django App"
wait
sudo /usr/local/lib/uwsgi/uwsgi --ini uwsgi.ini
echo "uWSGI for django-websocket-redis"
wait
sudo /usr/local/lib/uwsgi_ws/uwsgi --ini uwsgi_ws.ini

wait
echo "NGINX"
sudo cp textress.conf /etc/nginx/sites-enabled/textress.conf
wait
sudo service nginx restart

echo "Check uWSGI process count"
wait
sleep 5s
ps aux | grep uwsgi
