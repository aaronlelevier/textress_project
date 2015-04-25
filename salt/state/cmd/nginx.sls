cmd_update:
    cmd.script:
        - source: salt://cmd/file/nginx.sh
        - watch:
            - file: /opt/django/salt/state/cmd/file/nginx.sh
