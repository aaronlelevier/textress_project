cmd_update:
  cmd.run:
    - names:
      - ufw allow 80/tcp
      - ufw allow 443/tcp
      - ufw status


collectstatic:
  cmd.run:
    - name: /root/.virtualenvs/textress/bin/python manage.py collectstatic
    - cwd: /opt/django/textress
    - require:
      - sls: git
