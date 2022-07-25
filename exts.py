from celery import Celery

celery = Celery("prosimos_celery", include=['src.tasks'])