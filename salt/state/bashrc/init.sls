# The toplevel name of the file: `/root/.bashrc` is the destination file
# `source` -> the source file used to populate the destination file
/root/.bashrc:
  file.managed:
    - source: salt://bashrc/bashrc
    - user: root
    - group: root
    - mode: 0644


# Load any changed environ VARs
cmd.run:
  - name: source /root/.bashrc
  - watch:
    - file: /root/.bashrc
