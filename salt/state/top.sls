base:
  'salt':
    - cmd.salt

  '*':
    - cmd
    - bashrc
    - packages
    - virtualenv
    - environ
    - git
    - keys
    - users

  'roles:rproxy':
    - cmd.rproxy
    - keys.ssl

  'roles:appserver':
    - redis
    - rabbitmq
    - uwsgi

  'roles:database':
    - postgres
