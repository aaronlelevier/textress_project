include:
    - packages

python-pip:
    pkg.installed

upgrade_pip:
    cmd.run:
        - name: easy_install -U pip
        - require: 
            -pkg: python-pip

/opt/django/requirements.txt:
    file.managed:
        - source: salt://pip/requirements.txt
  
pip:
    pip.installed:
        - requirements: salt://pip/requirements.txt
        - require: 
            - sls: packages
            - file: /opt/django/requirements.txt
            - cmd: upgrade_pip
