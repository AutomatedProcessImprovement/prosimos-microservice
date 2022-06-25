from flask import abort, request, send_file
from flask_restful import Resource
from flasgger import swag_from
import os
import tempfile

from src.tasks import discovery_task

class DiscoveryApiHandler(Resource):
  @swag_from('./../swagger/discovery_post.yml', methods=['POST'])
  def post(self):
    try:
      files_data = request.files
      logs_file = files_data.get('logsFile')
      model_file = files_data.get('bpmnFile')

      curr_dir_path = os.path.abspath(os.path.dirname(__file__))
      celery_data_path = os.path.abspath(os.path.join(curr_dir_path, '..', 'celery/data'))
      
      logs_ext = logs_file.filename.split(".")[-1]
      logs_temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix="."+logs_ext, prefix="input_logs_", delete=False, dir=celery_data_path)
      logs_file.save(logs_temp_file.name)
      logs_filename = logs_temp_file.name.split('/')[-1]

      model_ext = model_file.filename.split(".")[-1]
      model_temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix="."+model_ext, prefix="model_", delete=False, dir=celery_data_path)
      model_file.save(model_temp_file.name)
      model_filename = model_temp_file.name.split('/')[-1]

      res = discovery_task.delay(logs_filename, model_filename)

      return res.id

      # return send_file(res_temp_file.name,
      #           mimetype="application/json",
      #           attachment_filename="parameters.json", as_attachment=True)

    except Exception as e:
      print(e)
      response = {
        "displayMessage": "Something went wrong"
      }

      return response, 500
