include:
    - uwsgi

supervisor:
    pkg:
        - installed
        - name: supervisor
    cmd.run:
        - name: supervisord -c /opt/django/salt/state/supervisord/appserver/supervisord.conf
        - require:
            - pkg: supervisor
        - watch:
            - file: uwsgi
