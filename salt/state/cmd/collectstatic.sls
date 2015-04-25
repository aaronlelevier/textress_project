include:
    - git

collectstatic:
    cmd.run:
        - name: python manage.py collectstatic
        - cwd: /opt/django/textress
        - require:
            - sls: git