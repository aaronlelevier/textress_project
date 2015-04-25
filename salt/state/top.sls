base:
    '*':
        - cmd
        - bashrc
        - packages
        - pip
        - environ
        - git
        - keys
        - users

    'salt':
        - cmd.salt

    'roles:rproxy':
        - cmd.rproxy
        - cmd.collectstatic
        - keys.ssl
        - supervisord.rproxy

    'roles:appserver':
        - uwsgi
        - supervisord.appserver

    'roles:database':
        - postgres