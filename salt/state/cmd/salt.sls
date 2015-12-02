include:
  - git

update-salt-states:
  cmd.run:
    - name: cp -r /opt/django/salt/state/* /srv/salt
    - require:
      - sls: git


copy-pip-requirements:
  cmd.run:
    - name: cp /opt/django/requirements.txt /srv/salt/virtualenv/requirements.txt
