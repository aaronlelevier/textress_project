from textress import celery_app

@celery_app.task
def hello_world():
    print('Hello World')