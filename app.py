from flask import Flask, jsonify
from flask_restful import Api
from flask_cors import CORS
from api.FileApiHandler import FileApiHandler
from api.ProsimosApiHandler import ProsimosApiHandler

app = Flask(__name__, static_url_path='', static_folder='frontend/build')

@app.errorhandler(500)
def handle_exception(err):
    print(str(err))
    response = {
        "displayMessage": "A server error occurred",
        "error": str(err)
    }

    return response, 500

app.register_error_handler(500, handle_exception)
api = Api(app, prefix='/api')
CORS(app)

@app.route("/", defaults={'path':''})
def serve(path):
    return "hello, world"

api.add_resource(ProsimosApiHandler, '/prosimos')
api.add_resource(FileApiHandler, '/file')
