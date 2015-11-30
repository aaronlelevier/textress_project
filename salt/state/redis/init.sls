install-redis:
  pkg.installed:
    - name: redis

redis:
  service.running:
    - enable: True
    - reload: True
