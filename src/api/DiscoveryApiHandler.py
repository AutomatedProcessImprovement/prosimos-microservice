from flask import make_response, request
from flask_restful import Resource
from flasgger import swag_from
import os
import tempfile

from src.tasks import discovery_task

class DiscoveryApiHandler(Resource):
  def __saveFile(self, fileStorage, prefix, filePath):
      file_ext = fileStorage.filename.split(".")[-1]
      temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix="."+file_ext, prefix=prefix, delete=False, dir=filePath)
      fileStorage.save(temp_file.name)
      filename = temp_file.name.split('/')[-1]

      return filename
  
  @swag_from('./../swagger/discovery_post.yml', methods=['POST'])
  def post(self):
    try:
      files_data = request.files
      logs_file = files_data.get('logsFile')
      model_file = files_data.get('bpmnFile')

      curr_dir_path = os.path.abspath(os.path.dirname(__file__))
      celery_data_path = os.path.abspath(os.path.join(curr_dir_path, '..', 'celery/data'))
      
      logs_filename = self.__saveFile(logs_file, "input_logs_", celery_data_path)
      model_filename = self.__saveFile(model_file, "model_", celery_data_path)

      # run task locally, do not connect to AMQP
      # if (os.environ.get("FLASK_ENV", "development") == "development"):
      #   task_response = discovery_task(logs_filename, model_filename)

      task = discovery_task.delay(logs_filename, model_filename)
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
