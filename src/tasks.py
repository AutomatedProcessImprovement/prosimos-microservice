from celery.utils.log import get_task_logger
import tempfile
import os

from bpdfr_discovery.log_parser import preprocess_xes_log

from factory import create_celery, create_app

logger = get_task_logger(__name__)
celery = create_celery(create_app())

@celery.task(name='discovery_task')
def discovery_task(logs_filename, model_filename):
    logger.info(f'Logs file: {logs_filename}')
    logger.info(f'Model file: {model_filename}')
    
    curr_dir_path = os.path.abspath(os.path.dirname(__file__))
    celery_data_path = os.path.abspath(os.path.join(curr_dir_path, 'celery/data'))

    logs_path = os.path.abspath(os.path.join(celery_data_path, logs_filename))
    model_path = os.path.abspath(os.path.join(celery_data_path, model_filename))
    
    res_temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".json", prefix="discovery_results_", delete=False, dir=celery_data_path)

    [granule, conf, supp, part, adj_calendar] = [60, 0.1, 0.9, 0.6, True]

    _ = preprocess_xes_log(logs_path,
                                    model_path,
                                    res_temp_file.name, granule, conf, supp, part,
                                    adj_calendar)

    logger.info(res_temp_file.name)

    filename = res_temp_file.name.split('/')[-1]
    
    return { "discovery_res_filename": filename }
