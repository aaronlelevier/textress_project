# Installs python 2.7.10 from source w/ required Ubuntu packages

# Should this block of "packages" be put in 'package state.sls'?
python-2.7.10-required-packages:
  pkg.installed:
    - pkgs:
      - build-essential
      - checkinstall
      - libreadline-gplv2-dev
      - libncursesw5-dev
      - libssl-dev
      - libsqlite3-dev
      - tk-dev
      - libgdbm-dev
      - libc6-dev
      - libbz2-dev


install-python-2.7.10-from-tarball:
  cmd.run:
    - name: |
        wget https://www.python.org/ftp/python/2.7.10/Python-2.7.10.tgz && \
        tar xzf Python-2.7.10.tgz && cd Python-2.7.10 && \
        ./configure && make altinstall
    - cwd: /usr/src
