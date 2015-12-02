include:
  - packages


# virtualenv PIP installs
/root/.virtualenvs/textress:
  virtualenv.managed:
    - python: /usr/local/bin/python2.7
    - requirements: salt://virtualenv/requirements.txt
    - require:
      - sls: packages
