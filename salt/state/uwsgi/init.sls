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
    service.running:
        - name: uwsgi
        - enable: true
        - require:
            - pkg: uwsgi
            - file: uwsgi
        - watch:
            - file: uwsgi