import zipfile
from flask import make_response, request
from flask_restful import Resource
from flasgger import swag_from
import os
import tempfile
from zipfile import ZipFile

from src.tasks import discovery_task

class DiscoveryApiHandler(Resource):
  def __saveFile(self, fileStorage, prefix, filePath):
      file_ext = fileStorage.filename.split(".")[-1]
      temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix="."+file_ext, prefix=prefix, delete=False, dir=filePath)
      fileStorage.save(temp_file.name)
      filename = temp_file.name.split(os.sep)[-1]

      return filename


  def __saveFileFromZip(self, logs_file, folder_to_save):
    with ZipFile(logs_file._file, 'r') as zf:
      namelist = zf.namelist()
      only_log_file = [filename for filename in namelist if not filename.startswith("__MACOSX")]
      if (len(only_log_file) != 1):
        print("WARNING: Expecting only one file inside the zip")
        #TODO: throw exception
      else:
        zip_log_filename = only_log_file[0]
        prefix = "input_logs_"
        file_ext = zip_log_filename.split(".")[-1]
        temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix="."+file_ext, prefix=prefix, delete=False, dir=folder_to_save)
        with open(temp_file.name, "wb") as f:
          f.write(zf.read(zip_log_filename))
        
        filename = temp_file.name.split(os.sep)[-1]
        return filename

  
  @swag_from('./../swagger/discovery_post.yml', methods=['POST'])
  def post(self):
    try:
      files_data = request.files
      logs_file = files_data.get('logsFile')
      model_file = files_data.get('bpmnFile')

      curr_dir_path = os.path.abspath(os.path.dirname(__file__))
      celery_data_path = os.path.abspath(os.path.join(curr_dir_path, '..', 'celery/data'))
      
      # in_logs_mimetype = logs_file.mimetype.split("/")[-1]
      print(logs_file.mimetype)

      is_zipfile = zipfile.is_zipfile(logs_file)
      
      logs_filename = \
        self.__saveFileFromZip(logs_file, celery_data_path) if is_zipfile else \
        self.__saveFile(logs_file, "input_logs_", celery_data_path)

      model_filename = self.__saveFile(model_file, "model_", celery_data_path)

      logs_extension = logs_filename.split(".")[-1]
      is_xes = False
      if (logs_extension == 'csv'):
        is_xes = True
      elif (logs_extension != 'xes'):
          print(f"WARNING: Extension {logs_extension} of the log file is not supported")

      task = discovery_task.delay(logs_filename, model_filename, is_xes)
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
