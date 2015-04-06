To start all background process, in separate terminals run
----------------------------------------------------------
`./manage.py runserver`

`rabbitmq-server`

`redis-server`

`celery -A demo worker -l debug`

Docker
------
CMD:
    docker images | grep "ubuntu" | awk '{print $3}' | xargs docker rmi -f

Reference:
    http://stackoverflow.com/questions/17236796/how-to-remove-old-docker-containers

Dockerfile Gist
    (if I am going to use a Dockerfile, and not django-compose??)
    https://gist.github.com/aronysidoro/db9efbbd1419e2e36d6f