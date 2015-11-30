# 'apt-get upgrade' needs a 'no input' flag

global-updates:
  cmd.run:
    - name: |
      apt-get update
      apt-get upgrade
