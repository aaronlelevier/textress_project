python-pip:
    pkg.installed

/opt/django/requirements.txt:
    file.managed:
        - source: salt://django/requirements.txt
  
django:
    pip.installed:
        - requirements: salt://django/requirements.txt
        - require: 
            - pkg: python-pip
            - file: /opt/django/requirements.txt