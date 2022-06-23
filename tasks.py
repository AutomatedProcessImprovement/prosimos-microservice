from exts import celery
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery.task(name='discovery_task')
def discovery_task(x, y):
    logger.info('Discovering the scenario parameters: %(x) and %(y)')
    return x + y