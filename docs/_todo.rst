2015-07-12
----------
:todo:
    - refactor GuestDetailView.html
:manage_users:
    where is the "add a Mgr" view?
:setup_images_as_attrs:
    - for User / Guest - set their profile pick as an image
        - use ``Gimp`` to generate 2 default pics


2015-07-08
----------
:Next:
    :form_styling:
        - add a red * for required to all "django-angular" forms
        - Date fields need a ``Date Picker``
    :styling:
        - Message Detail Page 
            - add styling and correct links
        - User Profile Page 
            - (make this share w/ the "Manage User Profile" page)
        - Avatars - instead of pics for Users
        - Guests - have a default empty Guest Pic
        - Message
            - display time stamp below like iOS
            - change color to blue to match color scheme



2015-07-08
----------
:mixins:
    run tests for: account/concierge/main/payment .. views
    finish: 
        - payment.mixin tests
        - main.mixin tests - for mixins moved to 'main' app

:concierge:
    - tests need refactoring, currently (14) test fails

2015-07-07
----------
:Next:
    - Refactor "Http404" errors to "PermissionDenied" errors

        - display a more meaningful. ex- "No Hotel registered, create a Hotel for your Account."
        - Make sublcasses of "PermissionDenied" exceptions that generate "django messages" and raise 
        the error to display the "403.html" page.

    - move "Mixin" locations based on Model Obj of that App.

    - continue Payment Logic / testing


2015-07-06
----------
:Next:
    - Payment Tests: Focus on componenet based tests, and only test ea. component 1x


2015-07-03
----------
:Next:
    - confirm all "Manage User Views" work, tested, render, etc
    

2015-07-03
----------
:Next: 
    - add tests for: MgrUserUpdateView
    - make a summary of all data for the User, and add tests for: MgrUserDetailView
    - use TDD to finish "manage-user" views

Manage other Users Views

- ``MgrUserListView``

    - Add to "base-sidebar.html"
    - Check if View renders?
    - Will be an Angular App / View


2015-07-02
----------
use Error messages to redirect to the relevant page, i.e. payment.mixins.HotelUserMixin


2015-04-15
----------
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
