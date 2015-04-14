git:
    pkg.installed: []
    
bitbucket.org:
    ssh_known_hosts:
        - present
        - user: root
        - fingerprint: 97:8c:1b:f2:6f:14:6b:5c:3b:ec:aa:46:46:74:7c:40

github.com:
    ssh_known_hosts:
        - present
        - user: root
        - fingerprint: 16:27:ac:a5:76:28:2d:36:63:1b:56:4d:eb:df:a6:48

git-website-prod:
    git.latest:
        - name: git@bitbucket.org:pyaaron/textra_17.git
        - rev: latest
        - target: /opt/django
        - identity: /root/.ssh/id_rsa
        - require:
            - pkg: git
            - ssh_known_hosts: bitbucket.org