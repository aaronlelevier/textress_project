### appserver has a python3 virtualenv used to serve django app

include:
    - packages

python3-pip:
    pkg.installed

upgrade_pip:
    cmd.run:
        - name: easy_install -U pip
        - require: python3-pip

/opt/django/salt/state/pip/appserver/requirements.txt:
    file.managed:
        - source: salt://pip/appserver/requirements.txt:
  
pip:
    pip.installed:
        - requirements: salt://pip/appserver/requirements.txt:
        - require: 
            - sls: packages
            - file: /opt/django/salt/state/pip/appserver/requirements.txt
            - cmd: upgrade_pip
