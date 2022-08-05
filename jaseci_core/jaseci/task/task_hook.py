import json
from multiprocessing import Process
from uuid import uuid4

from ..utils.utils import logger
from .task_config import QUIET
from .tasks import queue, dynamic_request
from celery import Celery

from django_celery_results.models import TaskResult


class task_hook:

    app = None
    inspect = None
    worker = None
    scheduler = None
    registered_task = {}

    _queue = None
    _dynamic_request = None

    def __init__(self):
        if task_hook.app is None:
            try:
                self.__celery()
                if task_hook.inspect.ping() is None:
                    self.__tasks()
                    self.__worker()
                    self.__scheduler()
            except Exception as e:
                logger.error(f"Resetting celery as it returns '{e}'")
                task_hook.app = None

    def __celery(self):
        task_hook.app = Celery("celery")
        task_hook.app.config_from_object("jaseci.task.task_config")
        task_hook.inspect = task_hook.app.control.inspect()

    def __worker(self):
        task_hook.worker = Process(target=task_hook.app.Worker(quiet=QUIET).start)
        task_hook.worker.daemon = True
        task_hook.worker.start()

    def __scheduler(self):
        task_hook.scheduler = Process(target=task_hook.app.Beat(quiet=QUIET).run)
        task_hook.scheduler.daemon = True
        task_hook.scheduler.start()

    def __tasks(self):
        task_hook._queue = task_hook.app.register_task(queue())
        task_hook._dynamic_request = task_hook.app.register_task(dynamic_request())

    def inspect_tasks(self):
        return {
            "scheduled": task_hook.inspect.scheduled(),
            "active": task_hook.inspect.active(),
            "reserved": task_hook.inspect.reserved(),
        }

    def get_by_task_id(self, task_id):
        task = task_hook.app.AsyncResult(task_id)

        res = {"state": task.state}

        if task.ready():
            task_result = TaskResult.objects.get(task_id=task_id).result
            try:
                res["result"] = json.loads(task_result)
            except ValueError as e:
                res["result"] = task_result

        return res

    def terminate_worker(self):
        task_hook.worker.terminate()

    def terminate_scheduler(self):
        task_hook.scheduler.terminate()

    def task_hook_ready(self):
        return not (task_hook.app is None)

    def queue(self, caller, api_name, **kwargs):

        print("###############")
        print(caller)
        print(api_name)
        print(kwargs)
        print("###############")

        return task_hook._queue.delay(caller, api_name, {}).task_id

    def consume(caller, api_name, **kwargs):

        print("###############")
        print(caller)
        print(api_name)
        print(kwargs)
        print("###############")

        # return que["method"](**que["kwargs"])
