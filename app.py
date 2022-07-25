from flask_restful import Api
from factory import create_app, create_swagger
from src.api.FileApiHandler import FileApiHandler
from src.api.SimulationApiHandler import SimulationApiHandler
from src.api.DiscoveryApiHandler import DiscoveryApiHandler
from src.api.TaskApiHandler import TaskApiHandler

app = create_app()
api = Api(app, prefix='/api')
swagger = create_swagger(app)

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
api.add_resource(TaskApiHandler, '/task')
