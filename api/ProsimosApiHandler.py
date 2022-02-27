from flask_restful import Resource

class ProsimosApiHandler(Resource):
  def get(self):
    return "prosimos get"
