# global PIP installs

install-pip:
  cmd.run:
    - name: |
      easy_install -U pip==7.1.0
      pip install virtualenv
