/etc/nginx/ssl/textress.com.chained.crt:
    file.managed:
        - source: salt://nginx/files/textress.com.chained.crt
        - makedirs: true
        - user: root
        - group: root
        - mode: 0400

/etc/nginx/ssl/textress.com.key:
    file.managed:
        - source: salt://nginx/files/textress.com.key
        - makedirs: true
        - user: root
        - group: root
        - mode: 0400
