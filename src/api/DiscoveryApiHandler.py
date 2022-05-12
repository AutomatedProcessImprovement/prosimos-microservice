from flask import abort, request, send_file
from flask_restful import Resource
import tempfile
from flasgger import swag_from

from bpdfr_discovery.log_parser import preprocess_xes_log

class DiscoveryApiHandler(Resource):
  @swag_from('./../swagger/discovery_post.yml', methods=['POST'])
  def post(self):
    try:
      dir_prefix = "/tmp"
      files_data = request.files
      logs_file = files_data.get('logsFile')
      model_file = files_data.get('bpmnFile')

      logs_temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".json", prefix="input_logs_", delete=False, dir=dir_prefix)
      with open(logs_temp_file.name, 'wb') as f:
        logs_file.save(f)

      model_temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".json", prefix="model_", delete=False, dir=dir_prefix)
      with open(model_temp_file.name, 'wb') as f:
        model_file.save(f)

      res_temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".json", prefix="discovery_results_", delete=False, dir=dir_prefix)

      print(logs_temp_file)
      print(logs_temp_file.name)

      [granule, conf, supp, part, adj_calendar] = [60, 0.1, 0.7, 0.3, True]

      _ = preprocess_xes_log(logs_temp_file.name,
                                        model_temp_file.name,
                                        res_temp_file.name, granule, conf, supp, part,
                                        adj_calendar)

      return send_file(res_temp_file.name,
                mimetype="application/json",
                attachment_filename="parameters.json", as_attachment=True)

    except Exception as e:
      print(e)
      response = {
        "displayMessage": "Something went wrong"
      }

      return response, 500
