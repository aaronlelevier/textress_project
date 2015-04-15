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

    # main django application server
    'salt':
        - nginx

    # postres db server
    'minion':
        - postgres