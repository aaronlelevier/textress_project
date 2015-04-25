supervisor:
    pkg.installed

/opt/django/salt/state/supervisord/appserver/supervisord.conf

update-supervisor:
    cmd.run:
        - name: supervisord -c /opt/django/salt/state/supervisord/appserver/supervisord.conf
        - require:
            - pkg: supervisor
        - watch:
            - file: /opt/django/salt/state/uwsgi/uwsgi.ini