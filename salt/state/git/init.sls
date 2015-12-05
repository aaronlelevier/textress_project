include:
- keys

git:
    pkg.installed

bitbucket.org:
    ssh_known_hosts:
        - present
        - user: root
        - fingerprint: 6b:90:14:da:0e:a6:d4:ed:d4:98:bc:6a:c2:0e:8c:05

git-website-prod:
    git.latest:
        - name: git@bitbucket.org:pyaaron/textra_17.git
        - rev: master
        - target: /opt/django
        - identity: /root/.ssh/id_rsa
        - require:
            - sls: keys
            - pkg: git
            - ssh_known_hosts: bitbucket.org