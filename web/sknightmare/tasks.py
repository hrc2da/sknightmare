from celery import Celery
@celery.task
def add_together(a, b):
    print('adding')
    return a + b