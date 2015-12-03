cmd_update:
  cmd.run:
    - names:
      - ufw allow 80/tcp
      - ufw allow 443/tcp
      - ufw status

include:
  - git

collectstatic:
  cmd.run:
    - name: python manage.py collectstatic
    - cwd: /opt/django/textress
    - require:
      - sls: git
