include:
    - git

update-salt-states:
    cmd.run:
        - name: cp -r /opt/django/salt/state/* /srv/salt
        - require:
            - sls: git
