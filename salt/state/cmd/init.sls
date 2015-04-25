cmd_update:
    cmd.script:
        - source: salt://cmd/file/init.sh
        - watch:
            - file: /opt/django/salt/state/cmd/file/init.sh
