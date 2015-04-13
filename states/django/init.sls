python-pip:
  pkg.installed
  
django:
    pip.installed:
        - requirements: salt://django/requirements.txt
        - require: 
            - pkg: python-pip