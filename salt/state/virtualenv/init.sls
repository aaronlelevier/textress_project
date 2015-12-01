include:
  - packages


copy-pip-requirements:
  cmd.run:
    - name: cp /opt/django/requirements.txt /srv/salt/pip/requirements.txt


/root/.virtualenvs/textress:
  virtualenv.managed:
    - requirements: salt://pip/requirements.txt
    - require:
      - sls: packages