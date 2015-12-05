### Install Nginx and configure it as a reverse proxy, pulling the IPs of
### the app servers from the Salt Mine.

nginx-rproxy:
  # Install Nginx
  pkg:
    - installed
    - name: nginx
  # Place a customized Nginx config file
  file:
    - managed
    - source: salt://nginx/files/textress.conf.jin
    - name: /opt/django/textress.conf
    - template: jinja
    - require:
      - pkg: nginx-rproxy
  # Ensure Nginx is always running.
  # Restart Nginx if the config file changes.
  service:
    - running
    - enable: True
    - name: nginx
    - require:
      - pkg: nginx-rproxy
    - watch:
      - file: nginx-rproxy
  # Restart Nginx for the initial installation.
  cmd:
    - run
    - name: |
          rm /etc/nginx/sites-enabled/default && \
          ln -s /opt/django/textress.conf /etc/nginx/sites-enabled/textress.conf && \
          sudo /etc/init.d/nginx restart
    - require:
      - file: nginx-rproxy
