from flask import request, make_response
from flask_restful import Resource
import tempfile
from flasgger import swag_from
import os

from src.tasks import simulation_task

class SimulationApiHandler(Resource):

  def __saveFile(self, fileStorage, prefix, filePath):
    file_ext = fileStorage.filename.split(".")[-1]
    temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix="."+file_ext, prefix=prefix, delete=False, dir=filePath)
    fileStorage.save(temp_file.name)
    filename = temp_file.name.split('/')[-1]

    return filename

  @swag_from('./../swagger/simulation_post.yml', methods=['POST'])
  def post(self):
    try:
      form_date = request.form
      files_data = request.files
      num_processes = form_date.get('numProcesses')
      parameters_data = files_data.get('simScenarioFile')
      xml_data = files_data.get('modelFile')
      start_date = form_date.get('startDate')

      curr_dir_path = os.path.abspath(os.path.dirname(__file__))
      celery_data_path = os.path.abspath(os.path.join(curr_dir_path, '..', 'celery/data'))

      json_file = self.__saveFile(parameters_data, "params_", celery_data_path)
      bpmn_file = self.__saveFile(xml_data, "bpmn_model_", celery_data_path)

      task = simulation_task.delay(bpmn_file, json_file, num_processes, start_date)
      task_id = task.id

      task_response = f"""{{
        "TaskId": "{task_id}"
}}"""

      response = make_response(task_response)
      response.headers['content-type'] = 'application/json'
      return response

    except Exception as e:
      print(e)
      response = {
        "displayMessage": "Something went wrong"
      }

      return response, 500
