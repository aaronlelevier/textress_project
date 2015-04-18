base:
    # main django/pip reqs, apt-get packages
    '*':
        - bashrc
        - django
        - packages
        - environ
        - git
        - keys
        - users
        - cmd

    'nginx-rproxy':
        - nginx

    'appserver-01':
        - uwsgi # todo: build this

    'database-01':
        - postgres