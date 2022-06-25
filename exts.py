from celery import Celery

celery = Celery("prosimos_celery", backend='rpc://', include=['src.tasks'])