include:
  - git

update-salt-states:
  cmd.run:
    - name: cp -r /opt/django/salt/state/* /srv/salt
    - require:
      - sls: git

# put project 'reqs.txt' in 'salt dir' so can pip
# install them on minion appserver(s)
copy-pip-requirements:
  cmd.run:
    - name: cp /opt/django/requirements.txt /srv/salt/virtualenv/requirements.txt
