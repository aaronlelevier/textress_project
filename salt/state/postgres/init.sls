install-postgresql:
    pkg.installed:
        - pkgs: 
            - postgresql-9.3
            - postgresql-contrib
            - postgresql-client
            - postgresql-server-dev-9.3

db:
    postgres_database.present:
        - name: {{ grains['T17_DB_NAME']}}
        - db_user: {{ grains['T17_DB_USER']}}
        - db_password: {{ grains['T17_DB_PASSWORD']}}
        - db_port: 5432
        - user: {{ grains['T17_DB_USER']}}

run-postgresql:
    service.running:
        - enable: true
        - name: postgresql-9.3
        - require:
            - pkg: install-postgresql