from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from celery.schedules import crontab
import os

from exts import celery

def create_app():
    app = Flask(__name__)

    CORS(app)

    # swagger config
    app.config["SWAGGER"] = {
        "title": "Prosimos API",
        "uiversion": 3,
        "openapi": "3.0.3",
        "specs": [
            {
                "version": "v1.0",
                "endpoint": "v1_spec",
                "route": "/v1.0",
            }
        ],
    }

    # celery config
    app.config["CELERY_BROKER_URL"] = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672/")
    app.config["CELERY_RESULT_BACKEND"] = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

    return app

def create_swagger(app):
    relative_path_to_template = "src/swagger/initial_components_schemas.yml"
    swagger = Swagger(app, template_file=relative_path_to_template)
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
        CELERY_BROKER_URL=app.config["CELERY_BROKER_URL"],
        CELERY_RESULT_BACKEND = app.config["CELERY_RESULT_BACKEND"],
        CELERY_RESULT_PERSISTENT=True,
        CELERY_ACCEPT_CONTENT = ["json"],
        CELERY_TASK_SERIALIZER = "json",
        CELERY_RESULT_SERIALIZER = "json",
        CELERY_IGNORE_RESULT = False,
        CELERY_TRACK_STARTED = True,
        CELERYBEAT_SCHEDULE = {
            "every-hour-celery-data-clear": {
                "task": "src.tasks.clear_celery_folder",
                "schedule": crontab(minute="0", hour="*/1"),
                "args": ()
            },
        }
    )
    celery.Task = ContextTask

    return celery
