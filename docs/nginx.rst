nginx
=====
# make unix websocket executable
chomod 0666 textress.sock

# test `conf` files
nginx -t

# start
sudo /etc/init.d/nginx start 

# restart
sudo /etc/init.d/nginx restart

# remove default
rm /etc/init/sites-enabled/default

# add textress.conf to sites enabled
ln -s /opt/django/textress.conf /etc/nginx/sites-enabled/textress.conf


nginx + uwsgi proxy test
------------------------
# port 9000 is forwarding to port 80

http://uwsgi-docs.readthedocs.org/en/latest/tutorials/Django_and_nginx.html#nginx-and-uwsgi-and-test-py

upstream django {
    server my.i.p.addr:9000 fail_timeout=0; 
}
server {
    listen 80;
    server_name example.com;

    location / {
        # uWSGI config
        uwsgi_pass textress; # name of the `upstream` server
        include /opt/django/uwsgi_params; # the uwsgi_params file you installed
    }
}

# reload nginx and run w/ uwsgi
sudo /etc/init.d/nginx restart
uwsgi --socket :9000 --wsgi-file test.py