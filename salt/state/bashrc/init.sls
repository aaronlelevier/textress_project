copy-bashrc:
    file.copy:
        - name: /srv/salt/bashrc/bashrc
        - source: /root/.bashrc
        - force: True
        - makedirs: True
        - user: root
        - group: root
        - mode: 0644

/root/.bashrc:
    file.managed:
        - user: root
        - group: root
        - mode: 0644
        - source: salt://bashrc/bashrc