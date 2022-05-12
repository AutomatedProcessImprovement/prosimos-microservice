from flask import abort, request, send_file
from flask_restful import Resource
from flasgger import swag_from

class FileApiHandler(Resource):
  @swag_from('./../swagger/file_get.yml', methods=['GET'])
  def get(self):
    try:
      file_path = request.args["fileName"]
      file_category = file_path.rsplit('_')[0]
      dir_prefix = "/tmp/"
      return send_file(dir_prefix + file_path,
                mimetype='text/csv',
                attachment_filename=f"{file_category}.csv",
                as_attachment=True)
    except FileNotFoundError as e:
      response = {
        "displayMessage": "The file was not found",
      }

      return response, 404
    except Exception as e:
      abort(500, e)
