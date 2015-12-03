# global PIP installs

install-pip:
  cmd.run:
    - names:
      - easy_install -U pip==7.1.0
      - pip install virtualenv
