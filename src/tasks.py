from io import StringIO
import json
from bpdfr_discovery.exceptions import NotXesFormatException
from bpdfr_simulation_engine.exceptions import InvalidBpmnModelException, InvalidLogFileException
from celery.utils.log import get_task_logger
import tempfile
import os
from datetime import datetime
import pandas as pd
import time

from bpdfr_discovery.log_parser import preprocess_xes_log
from bpdfr_simulation_engine.simulation_engine import run_simulation

from factory import create_celery, create_app

logger = get_task_logger(__name__)
celery = create_celery(create_app())

def __getJsonString(out):
    df_out = pd.read_csv(StringIO(out), skiprows=1)
    df_out_json = df_out.to_json(orient='records')
    return df_out_json

@celery.task(name='discovery_task')
def discovery_task(logs_filename, model_filename, is_xes):
    try: 
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
                                        adj_calendar,
                                        is_xes)

        logger.info(res_temp_file.name)

        filename = res_temp_file.name.split('/')[-1]
        
        return { "discovery_res_filename": filename }
    except (
        NotXesFormatException, 
        InvalidBpmnModelException, 
        InvalidLogFileException
    ) as error:
        print('An exception occurred: {}'.format(error))
        return {
            "success": False,
            "errorMessage": str(error)
        }
    except BaseException as error:
        print(f"An exception occurred: {str(error)}")
        raise Exception(str(error))

@celery.task(name='simulation_task')
def simulation_task(model_filename, params_filename, num_processes, start_date):
    logger.info(f'Model file: {model_filename}')
    logger.info(f'Params file: {params_filename}')
    logger.info(f'Num of instances: {num_processes}')
    logger.info(f'Starting at: {start_date}')

    date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%f%z")

    curr_dir_path = os.path.abspath(os.path.dirname(__file__))
    celery_data_path = os.path.abspath(os.path.join(curr_dir_path, 'celery/data'))

    model_path = os.path.abspath(os.path.join(celery_data_path, model_filename))
    params_path = os.path.abspath(os.path.join(celery_data_path, params_filename))

    # create result file for saving statistics
    stats_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", prefix="stats_", delete=False, dir=celery_data_path)
    stats_filename = stats_file.name.rsplit('/', 1)[-1]

    # create result file for saving logs
    logs_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", prefix="logs_", delete=False, dir=celery_data_path)
    logs_filename = logs_file.name.rsplit('/', 1)[-1]

    _ = run_simulation(model_path, params_path,
        total_cases=int(num_processes),
        stat_out_path=stats_file.name,
        log_out_path=logs_file.name,
        starting_at=date)
    
    with stats_file as f:
        contents = f.read()

    _, out2, out3, out4 = contents.split('\n""\n')

    df_out2_json = __getJsonString(out2)
    df_out3_json = __getJsonString(out3)
    df_out4_json = __getJsonString(out4)

    print(df_out2_json)

    return {
        "ResourceUtilization": json.dumps(df_out2_json),
        "IndividualTaskStatistics": json.dumps(df_out3_json),
        "OverallScenarioStatistics": json.dumps(df_out4_json),
        "StatsFilename": stats_filename,
        "LogsFilename": logs_filename
    }

@celery.task()
def clear_celery_folder():
    curr_dir_path = os.path.abspath(os.path.dirname(__file__))
    celery_data_path = os.path.abspath(os.path.join(curr_dir_path, 'celery/data'))
    
    now = time.time()
    deleted_files_count = 0

    for f in os.listdir(celery_data_path):
        if f == "README.md":
            continue

        file_path = os.path.join(celery_data_path, f)
        if os.path.isfile(file_path):
            if os.stat(file_path).st_mtime < now - 1 * 3600:
                # if the age of the file is bigger than 1 hour
                logger.info(f'{f} file removing ...')
                os.remove(file_path)
                deleted_files_count = deleted_files_count + 1

    logger.info(f'In total deleted: {deleted_files_count} file(s) ')
