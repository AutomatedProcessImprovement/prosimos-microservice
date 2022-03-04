from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from api.ProsimosApiHandler import ProsimosApiHandler

app = Flask(__name__, static_url_path='', static_folder='frontend/build')
api = Api(app)
CORS(app)

@app.route("/", defaults={'path':''})
def serve(path):
    return "hello, world"

api.add_resource(ProsimosApiHandler, '/prosimos')
