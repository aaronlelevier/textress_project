uwsgi:
  # Install uwsgi
  pkg:
    - installed
    - name: uwsgi
  # Place a customized uwsgi file
  file:
    - managed
    - source: salt://uwsgi/files/uwsgi.ini
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
