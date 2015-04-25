include:
    - nginx

supervisor:
    pkg:
        - installed
        - name: supervisor
    cmd.run:
        - name: supervisord -c /opt/django/salt/state/supervisord/rproxy/supervisord.conf
        - require:
            - pkg: supervisor
            - sls: nginx
        - watch:
            - file: nginx
