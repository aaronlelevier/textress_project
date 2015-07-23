# README

## Dev Cmds

To start all background process, in separate terminals run

```
# Django
./manage.py runserver

# For ws4redis
redis-server

# For incoming messages
cd /Applications
./ngrok http 8000

# not in use
rabbitmq-server

# nnot in use
celery -A demo worker -l debug
```

## App Notes

### Utils