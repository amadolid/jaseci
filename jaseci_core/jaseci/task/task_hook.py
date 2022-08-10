import json
from multiprocessing import Process, Manager
from uuid import uuid4
import uuid

from ..utils.utils import logger
from .task_config import QUIET
from .tasks import queue, dynamic_request
from celery import Celery


class task_hook:

    app = None
    inspect = None
    worker = None
    scheduler = None

    basic_master = None
    main_hook = None

    queues = {}
    registered_task = {}

    _queue = None
    _dynamic_request = None

    def __init__(self):

        if task_hook.app is None:

            task_hook.main_hook = self

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
        task_hook.queues = Manager().dict()

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
            task_result = self.get_task_result_data(task_id)
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

    def get_element(jid):

        # Already validated reason for bypassing read access check
        return task_hook.main_hook.get_obj("bypass", uuid.UUID(jid), True)

    def queue(self, wlk):
        queue_id = str(uuid4())

        task_hook.queues.update(
            {queue_id: {"wlk": wlk.jid, "proc": wlk._async_procedure}}
        )

        return task_hook._queue.delay(queue_id).task_id

    def consume(queue_id):

        que = task_hook.queues.pop(queue_id)
        wlk = task_hook.get_element(que["wlk"])

        # pre procedure
        for proc in que["proc"]:
            if proc[0] == "run":
                if not (proc[1][0] is None):
                    # parse start_node
                    proc[1][0] = task_hook.get_element(proc[1][0])
                resp = getattr(wlk, proc[0])(*proc[1])
            else:
                out = getattr(wlk, proc[0])(*proc[1])
                if proc[2]:
                    wlk = out

        return resp

    def get_basic_master():
        if task_hook.basic_master is None:
            task_hook.basic_master = task_hook.main_hook.generate_basic_master()

        return task_hook.basic_master

    def generate_basic_master(self):
        """Generate basic master"""

    def get_task_result_data(self, task_id):
        """Get TaskResult by task_id"""

        return "Django not initialized!"
