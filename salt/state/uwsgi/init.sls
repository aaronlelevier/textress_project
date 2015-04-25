### appserver uwsgi configuration

uwsgi:
    # Install uwsgi
    pkg:
        - installed
        - name: uwsgi
    # Place a customized uwsgi file
    file:
        - managed
        - source: salt://uwsgi/files/uwsgi.ini.jin
        - name: /opt/django/uwsgi.ini
        - template: jinja
        - require:
            - pkg: uwsgi
    # Ensure uwsgi is always running.
    # Restart uwsgi if the config file changes.
    service:
        - running
        - enable: True
        - name: uwsgi
        - require:
            - pkg: uwsgi
        - watch:
            - file: uwsgi
    # Restart uwsgi for the initial installation.
    cmd:
        - run
        - name: uwsgi --ini /opt/django/uwsgi.ini
        - require:
            - file: uwsgi