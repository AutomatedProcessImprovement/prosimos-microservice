from exts import celery
from flask import request
from flask_restful import Resource
from src.tasks import discovery_task

class TaskApiHandler(Resource):
  def get(self):
    task_id = request.args["taskId"]
    
    res = discovery_task.AsyncResult(task_id, app=celery)
    print(res.state)
    # print(res.get())
    return res.state
