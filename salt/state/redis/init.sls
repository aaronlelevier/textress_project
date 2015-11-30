install-redis:
  pkg.installed:
    - name: redis-server

redis:
  service.running:
    - enable: True
    - reload: True
