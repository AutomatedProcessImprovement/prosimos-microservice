import pandas as pd
from io import StringIO
from flask import request, make_response
from flask_restful import Resource
from bpdfr_simulation_engine.simulation_engine import run_simulation
from datetime import datetime
import tempfile as tfile

class ProsimosApiHandler(Resource):
  def __getJsonString(self, out):
    df_out = pd.read_csv(StringIO(out), skiprows=1)
    df_out_json = df_out.to_json(orient='records')
    return df_out_json

  def post(self):
    content = request.json
    numProcesses = content['numProcesses']
    startDate = content['startDate']
    jsonData = content['jsonData']
    xmlData = content['xmlData']

    json_path = "./temp_files/bimp_example.json" 
    # json_file = tfile.NamedTemporaryFile(mode="w+", suffix=".json", prefix="params_", delete=False, dir='/tmp')
    bpmn_file = tfile.NamedTemporaryFile(mode="w+", suffix=".bpmn", prefix="bpmn_model_", delete=False, dir='/tmp')
    stats_file = tfile.NamedTemporaryFile(mode="w+", suffix=".csv", prefix="stats_", delete=False, dir='/tmp')
    logs_file = tfile.NamedTemporaryFile(mode="w+", suffix=".csv", prefix="logs_", delete=False, dir='/tmp')
    logs_filename = logs_file.name.rsplit('/', 1)[-1]

    # TODO: uncomment when new json format will be handled correctly
    # with json_file as file_writter:
    #   json.dump(jsonData, file_writter)
    
    with bpmn_file as f:
      f.write(xmlData)

    date = datetime.strptime(startDate, "%Y-%m-%dT%H:%M:%S.%f%z")

    # run simulation
    _ = run_simulation(bpmn_file.name, json_path,
      total_cases=numProcesses,
      stat_out_path=stats_file.name,
      log_out_path=logs_file.name,
      starting_at=date)

    with stats_file as f:
      contents = f.read()

    _, out2, out3, out4 = contents.split('\n""\n')

    df_out2_json = self.__getJsonString(out2)
    df_out3_json = self.__getJsonString(out3)
    df_out4_json = self.__getJsonString(out4)

    str = f"""{{
            "Resource Utilization": {df_out2_json},
            "Individual Task Statistics": {df_out3_json},
            "Overall Scenario Statistics": {df_out4_json},
            "LogFileName": "{logs_filename}"
          }}"""

    response = make_response(str)
    response.headers['content-type'] = 'application/json'

    return response
