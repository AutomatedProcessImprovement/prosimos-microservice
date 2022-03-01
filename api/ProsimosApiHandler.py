from flask import request, jsonify
from flask_restful import Resource
from bpdfr_simulation_engine.simulation_engine import run_simulation

class ProsimosApiHandler(Resource):
  def post(self):
    content = request.json
    totalCases = content['totalCases']
    startingAt = content['startingAt']

    res = run_simulation("", "", 10)

    # TODO: call simulation here and return the result
    return jsonify({ "start": res, "t": totalCases })
