# required global PIP modules for 'Salt'

pip:
  pip.installed:
    - requirements: salt://pip/salt-requirements.txt
    - require: 
      - sls: pip.common
