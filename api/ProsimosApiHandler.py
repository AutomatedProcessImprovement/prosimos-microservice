import pandas as pd
from io import StringIO
from flask import request, make_response
from flask_restful import Resource
from bpdfr_simulation_engine.simulation_engine import run_simulation

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
    bpmn_path = "./temp_files/BIMP_example.bpmn"
    stat_out_path = "./temp_files/bimp_example_stat.csv"

    # TODO: uncomment when new json format will be handled correctly
    # with open(json_path, 'w') as file_writter:
    #   json.dump(jsonData, file_writter)

    with open(bpmn_path, 'w') as file_writter:
      file_writter.write(xmlData)

    # run simulation
    res = run_simulation(bpmn_path, json_path, total_cases=numProcesses, stat_out_path=stat_out_path)

    with open(stat_out_path) as f:
      contents = f.read()

    _, out2, out3, out4 = contents.split('\n""\n')

    df_out2_json = self.__getJsonString(out2)
    df_out3_json = self.__getJsonString(out3)
    df_out4_json = self.__getJsonString(out4)

    str = f"""{{
            "Resource Utilization": {df_out2_json},
            "Individual Task Statistics": {df_out3_json},
            "Overall Scenario Statistics": {df_out4_json}
          }}"""

    response = make_response(str)
    response.headers['content-type'] = 'application/json'
    return response
