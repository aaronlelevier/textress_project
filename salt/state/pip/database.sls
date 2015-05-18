python-pip:
    pkg.installed

upgrade_pip:
    cmd.run:
        - name: easy_install -U pip
        - require: python-pip
  
pip:
    pip.installed:
        - name: psycopg2>=2.6
        - require:
            - pkg: python-pip
            - cmd: upgrade_pip