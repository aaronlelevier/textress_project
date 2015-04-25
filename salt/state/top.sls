base:
    # update state from git repo
    'salt':
        - cmd.salt

    ## cmd
    '*':
        - cmd
    'roles:rproxy':
        - cmd.nginx

    '*':
        - bashrc
        - django
        - packages
        - environ
        - git
        - keys
        - users

    'nginx-rproxy':
        - nginx

    'appserver-01':
        - uwsgi # todo: build this

    'database-01':
        - postgres