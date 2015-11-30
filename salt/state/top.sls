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
    - uwsgi

  'roles:database':
    - postgres
