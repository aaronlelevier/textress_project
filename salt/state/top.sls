base:
  'salt':
    - cmd.salt

  '*':
    - cmd
    - bashrc
    - packages
    - pip
    - environ
    - git
    - keys
    - users

  'roles:rproxy':
    - cmd.rproxy
    - cmd.collectstatic
    - keys.ssl
    - supervisord.rproxy

  'roles:appserver':
    - redis
    - rabbitmq
    - uwsgi

  'roles:database':
    - postgres
