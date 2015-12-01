include:
  - packages


update-salt-pip-requirements:
  cmd.run:
    - name: cp /opt/django/requirements.txt /srv/salt/pip/requirements.txt


# pip:
#   pip.installed:
#     - requirements: salt://pip/requirements.txt
#     - require:
#       - sls: packages
#       - file: /opt/django/requirements.txt


/root/.virtualenvs/textress:
  virtualenv.managed:
    - requirements: salt://pip/requirements.txt
    - require:
      - sls: packages