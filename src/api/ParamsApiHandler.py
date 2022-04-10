from flask import abort, request, send_file
from flask_restful import Resource
import tempfile

from bpdfr_discovery.log_parser import preprocess_xes_log

class ParamsApiHandler(Resource):
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

      [granule, conf, supp, part, adj_calendar] = [60, 0.2, 0.8, 0.4, False]

      [diff_resource_profiles,
    arrival_time_dist,
    json_arrival_calendar,
    gateways_branching,
    task_res_dist,
    task_resources,
    diff_res_calendars,
    task_events,
    task_resource_events,
    id_from_name] = preprocess_xes_log(logs_temp_file.name,
                                        model_temp_file.name,
                                        res_temp_file.name, granule, conf, supp, part,
                                        adj_calendar)

      print(diff_res_calendars)
      return send_file(res_temp_file.name,
                mimetype="application/json",
                attachment_filename="parameters.json", as_attachment=True)

    except Exception as e:
      print(e)
      response = {
        "displayMessage": "Something went wrong"
      }

      return response, 500
