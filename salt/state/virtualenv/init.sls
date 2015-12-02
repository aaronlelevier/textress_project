include:
  - packages


/root/.virtualenvs/textress:
  virtualenv.managed:
    - requirements: salt://virtualenv/requirements.txt
    - require:
      - sls: packages