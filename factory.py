from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
import os

from exts import celery

def create_app():
    app = Flask(__name__)

    CORS(app)

    # swagger config
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

    # celery config
    app.config['CELERY_BROKER_URL'] = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672/")
    # app.config['CELERY_RESULT_BACKEND'] = 'amqp://myuser:mypassword@localhost:5672/myvhost'
    # app.config['event_serializer'] = 'pickle'
    # app.config['result_serializer'] = 'pickle'
    # app.config['task_serializer'] = 'pickle'
    # celery.conf.accept_content = ["json","pickle","yaml"]

    return app

def create_swagger(app):
    swagger = Swagger(app)
    return swagger


def create_celery(app):
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    # configure Celery
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL']
    )
    celery.Task = ContextTask

    return celery
