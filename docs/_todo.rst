4-15-15
-------
finish the end of the django/postgres SaltStack tutorial, and check if it works

link
    http://www.barrymorrison.com/2013/Apr/21/deploying-django-with-salt-now-with-postgresql/

steps needed:

- configure `/srv/salt/top.sls` for states to which servers

- worker minion server WITHOUT FOR NOW**
    with redis / rabbitmq

- push up local textress repo
- pull down to salt-master using state
- update nginx state.sls w/ service.running

- find out where nginx files are at

    :file:
        textress
    :location:
        /etc/nginx/sites-available/textress
    :links:
        /etc/nginx/sites-enabled/textress

    :file:
        django.conf
    :notes:
        ssl cert locations
            ssl_certificate /etc/nginx/ssl/www_textress_com.crt;
            ssl_certificate_key /etc/nginx/ssl/textress.com.key;

- then uWSGI
    
    - ini file: copy Dockerfile orig `ini` setup n c if that works
    - needed `socket` assignment still in .wsgi file

    - create a log dir / file for uwsgi here:
        /var/log/uwsgi/textress.log