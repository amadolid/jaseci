from multiprocessing import Manager
from uuid import UUID, uuid4
from celery import Celery
from celery.app.control import Inspect
from celery.backends.base import DisabledBackend

from jaseci.svc import CommonService, ServiceState as Ss
from .common import Queue, ScheduledWalker, ScheduledSequence
from .config import TASK_CONFIG

#################################################
#                   TASK APP                   #
#################################################


class TaskService(CommonService):

    ###################################################
    #                   INITIALIZER                   #
    ###################################################

    def __init__(self, hook=None):
        manager = Manager()
        self.lock = manager.Lock()
        self.queues = manager.dict()
        self.inspect: Inspect = None
        self.queue: Queue = None
        self.scheduled_walker: ScheduledWalker = None
        self.scheduled_sequence: ScheduledSequence = None

        super().__init__(hook)

    ###################################################
    #                     BUILDER                     #
    ###################################################

    def builder(self, hook=None):
        configs = self.build_settings(hook)
        enabled = configs.pop("enabled", True)

        if enabled:
            self.quiet = configs.pop("quiet", False)
            self.app = Celery("celery")
            self.app.conf.update(**configs)

            # -------------------- TASKS -------------------- #

            self.queue = self.app.register_task(Queue())
            self.scheduled_walker = self.app.register_task(ScheduledWalker())
            self.scheduled_sequence = self.app.register_task(ScheduledSequence())

            # ------------------ INSPECTOR ------------------ #

            self.inspect = self.app.control.inspect()
            self.ping()

            self.state = Ss.RUNNING

            # ------------------ PROCESS ------------------- #
            self.spawn_daemon(
                worker=self.app.Worker(quiet=self.quiet).start,
                scheduler=self.app.Beat(socket_timeout=None, quiet=self.quiet).run,
            )
        else:
            self.state = Ss.DISABLED

    ###################################################
    #              COMMON GETTER/SETTER               #
    ###################################################

    def get_by_task_id(self, task_id, wait=False):
        task = self.app.AsyncResult(task_id)

        if isinstance(task.backend, DisabledBackend):
            return {
                "status": "DISABLED",
                "result": "result_backend is set to disabled!",
            }

        ret = {"status": task.state}
        if task.ready():
            ret["result"] = task.result
        elif wait:
            ret["status"] = "SUCCESS"
            ret["result"] = task.get(disable_sync_subtasks=False)

        return ret

    def inspect_tasks(self):
        return {
            "scheduled": self.inspect.scheduled(),
            "active": self.inspect.active(),
            "reserved": self.inspect.reserved(),
        }

    def ping(self):  # will throw exception
        self.inspect.ping()
        self.app.AsyncResult("").result

    ###################################################
    #                     QUEUING                     #
    ###################################################

    def add_queue(self, wlk, nd, *args):
        queue_id = str(uuid4())

        self.lock.acquire()
        self.queues.update({queue_id: {"wlk": wlk, "nd": nd, "args": args}})
        self.lock.release()

        return self.queue.delay(queue_id).task_id

    def consume_queue(self, queue_id):
        self.lock.acquire()
        que = self.queues.pop(queue_id)
        self.lock.release()

        wlk = que.get("wlk")
        nd = que.get("nd")
        args = que.get("args")
        mast = wlk._h.get_obj_from_store(UUID(wlk._m_id))

        wlk._to_await = True

        resp = wlk.run(nd, *args)
        wlk.register_yield_or_destroy(mast.yielded_walkers_ids)

        return {"anchor": wlk.anchor_value(), "response": resp}

    ###################################################
    #                     CLEANER                     #
    ###################################################

    def reset(self, hook):
        self.terminate_daemon("worker", "scheduler")
        self.inspect = None
        super().reset(hook)

    def failed(self):
        super().failed()
        self.terminate_daemon("worker", "scheduler")

    ####################################################
    #                    OVERRIDDEN                    #
    ####################################################

    def build_config(self, hook) -> dict:
        return hook.service_glob("TASK_CONFIG", TASK_CONFIG)
