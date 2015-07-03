July 2
------
use Error messages to redirect to the relevant page, i.e. payment.mixins.HotelUserMixin

add "account" button to biz home page when logged in

make sure login/logout is working as expected

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

    * no "daemonize for now" b/c harder to kill uwsgi process


4-18-15
-------
TODO
    
    ssl cert for new server(s)?
    
    separate servers
        salt
        nginx-rproxy
        appserver-01
        database-01


- change Nginx / uWSGI config to run using Salt State

    :nodename:
        the server node name assigned by Salt

- db server config
    
    - hardcode db IP to django project & c if it runs under uwsgi
    - replace as a `salt.mine('roles:database')


May 27 AngJS Notes
------------------
threejs.org

awwwards

webgl

canvas

ng-infinite scroll

dribble

codrops
