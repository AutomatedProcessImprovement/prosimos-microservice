from flask import abort, request, send_file
from flask_restful import Resource

class FileApiHandler(Resource):
  def get(self):
    try:
      file_path = request.args["filePath"]
      dir_prefix = "/tmp/"
      return send_file(dir_prefix + file_path,
                mimetype='text/csv',
                attachment_filename='logs.csv',
                as_attachment=True)
    except FileNotFoundError as e:
      response = {
        "displayMessage": "The file was not found",
      }

      return response, 404
    except Exception as e:
      abort(500, e)
