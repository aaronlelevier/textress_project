install-redis:
  pkg.installed:
    - name: redis-server

redis-server:
  service.running:
    - enable: True
    - reload: True
