/root/.ssh/id_rsa.pub:
    file.managed:
        - source: salt://keys/id_rsa.pub
        - user: root
        - group: root
        - mode: 0400

/root/.ssh/id_rsa:
    file.managed:
        - source: salt://keys/id_rsa
        - user: root
        - group: root
        - mode: 0400