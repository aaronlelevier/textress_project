Account Detail Fields
---------------------
date
type
desc
credit
debit
balance


2015-08-02
----------
:Next:
    - Add other Cards to Test Data List
    - Connect HTML / CSS logic w/ View code
    - Add Tests

2015-08-02
----------
:Next:
    - card images as a separate table

        - Add DB table
        - use the same naming convention as Stripe.com

    - pretty up cards list
    - config Django Views.py to work w/ OneTimePayment Form Data

    # "add a card" below like first checkbox

2015-07-30
----------
:Goals:
    - Payment History (on 'right' side, like Twilio), shows dates of recent payments


2015-07-27
----------
:Next:
    - Billing

        - Deposit Funds 1x View

            - Use the Registration Payment look / template

        - Monthly Stmts ListView

        - Single Month Transactions DetailView

        - Handle Auto-Reload True/False

            - Put a single ``Hook`` in ``recharge`` Func to check this status
            and disable if Auto-Reload=False

        # Recent Payments Table

        # Context / Sub URLs

        # make this a single page Summary, and use Twilio like layout

        # Change Payment Settings View

    - mark as read when going to Guest's DetailView

    - change Deletes to ``deleted`` flag globally

    - move all TemplateTags to ``utils`` app?


2015-07-23
----------
:Goals:
    # payment Model app tests
    # try to instantiate StripeClient() by itself to see if I can retrieve a customer

        - i.e. cus_6Kys7xxfuithl0

:Goals:
    :testing:
        - refactor tests to make simpler
        - fix broken tests
    :phone_number:
        - make sure that I am debiting accounts when buying a new ph #
    :accounting:
        - daily charges n balances work
    :AngularJs:
        - global App - b/c need to display "unread messages" in the top of
        the navbar

            - Question: will this conflict w/ the django-angular app?  maybe...

:Questions:
    - Should most all ``Models`` have a ``hide`` field?

        - or change ``hide`` to ``deleted``?


2015-07-22
----------
:Goals:
    # test incoming Messages from SMS (remember to start n use / "ngrok")

    # give each guest a "last_message" object that stores 

        - last message text
        - last message time
        - read / unread status

    # add counter of messages that updates to "GuestMsgPreviewCtrl" GuestListView page

    # refactor ".rst" docs/ so that the code command sections are readable from the browser

    # ws4redis - see if it cat use Redis w/i the Js file for the promise?
    # refactor code w/ ``ws4redis`` w/i AngJs ``submitMessage()`` func call


2015-07-17
----------
:account_view:
    - use OOP w/ AngJs w/ cpanel Messages and GuestDetailMessages if possible
    - add message append to "cpanel"

:random:
    - DRF - order_by for messages

:get_message:
direction   | guest for msg     | other guests
----------------------------------------------
incoming    |       ok          |       ok
outgoing    |                   |


2015-07-14
----------
:cpanel_dashboard:
    - figure out how to push updates to "cpanel" and "navbar" when messages
    come in


2015-07-14
----------
:cpanel_dashboard:
    - message_divs:
        - guest name
        - most recent message
        - highlighted count of unread messages
        - datetime of last message sent

:profile_pics:
    - add 10 more total to choose from
    - find out why not loading? or make a static char field for now?


2015-07-12
----------
:next:
    :tests:
        - simple view tests for things changed on Sunday
    :dashboard:
        - add "guest quick add button"
        - conversation miny ``div``. 1 per Guest, w/ a count of their messages (Angular view)
        :notes:
            - do I want to add a "Notes" model per/ Guest, so the User's can take notes on their Guests?
                - this would be using REST w/ an Angular service to ``Add/View/Update``
                - could go on the ``GuestDetailView`` below their info.

:cpanel_home:
    - "guest quick add", recent conversations snippets
:delete_views:
    - only change ``hide=True``
:setup_images_as_attrs:
    - for User / Guest - set their profile pick as an image
        - use ``Gimp`` to generate 2 default pics


2015-07-08
----------
:Next:
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
