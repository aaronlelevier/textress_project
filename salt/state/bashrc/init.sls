/root/.bashrc:
    file.managed:
        - source: salt://bashrc/bashrc
        - user: root
        - group: root
        - mode: 0644