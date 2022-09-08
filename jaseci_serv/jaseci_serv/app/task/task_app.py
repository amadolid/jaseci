import json
from django_celery_results.models import TaskResult
from jaseci_serv.jaseci_serv.settings import TASK_CONFIG
from jaseci.app.task.task_app import task_app as ta


#################################################
#                 TASK APP ORM                  #
#################################################


class task_app(ta):
    def get_by_task_id(self, task_id):
        task = self.task().AsyncResult(task_id)

        ret = {"status": task.state}

        if task.ready():
            task_result = TaskResult.objects.get(task_id=task_id).result
            try:
                ret["result"] = json.loads(task_result)
            except ValueError:
                ret["result"] = task_result

        return ret

    def get_config(self, hook) -> dict:
        return hook.build_config("TASK_CONFIG", TASK_CONFIG)
