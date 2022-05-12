from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flasgger import Swagger
from src.api.FileApiHandler import FileApiHandler
from src.api.SimulationApiHandler import SimulationApiHandler
from src.api.DiscoveryApiHandler import DiscoveryApiHandler

app = Flask(__name__)
api = Api(app, prefix='/api')
CORS(app)
app.config['SWAGGER'] = {
    'title': 'Prosimos API',
    'uiversion': 3,
    "specs": [
        {
            "version": "v1.0",
            "endpoint": 'v1_spec',
            "route": '/v1.0',
        }
    ]
}
swagger = Swagger(app)

@app.errorhandler(500)
def handle_exception(err):
    print(str(err))
    response = {
        "displayMessage": "A server error occurred",
        "error": str(err)
    }

    return response, 500

app.register_error_handler(500, handle_exception)

@app.route("/", defaults={'path':''})
def serve(path):
    return "hello, world"

api.add_resource(SimulationApiHandler, '/simulate')
api.add_resource(FileApiHandler, '/simulationFile')
api.add_resource(DiscoveryApiHandler, '/discovery')
