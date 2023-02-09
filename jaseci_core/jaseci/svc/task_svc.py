from celery import Celery
from celery.app.control import Inspect
from celery.backends.base import DisabledBackend

from jaseci.jsorc import JsOrc
from jaseci.svc.common_svc import CommonService
from .task import Queue, ScheduledWalker, ScheduledSequence

#################################################
#                   TASK APP                   #
#################################################


@JsOrc.service(
    name="task",
    config="TASK_CONFIG",
    priority=0,
    proxy=True,
)
class TaskService(CommonService):
    ###################################################
    #                   INITIALIZER                   #
    ###################################################

    def __init__(self, config: dict, manifest: dict):
        self.inspect: Inspect = None
        self.queue: Queue = None
        self.scheduled_walker: ScheduledWalker = None
        self.scheduled_sequence: ScheduledSequence = None

        super().__init__(config, manifest)

    ###################################################
    #                     BUILDER                     #
    ###################################################

    def run(self):
        self.app = Celery("celery")
        self.app.conf.update(**self.config)

        # -------------------- TASKS -------------------- #

        self.queue = self.app.register_task(Queue())
        self.scheduled_walker = self.app.register_task(ScheduledWalker())
        self.scheduled_sequence = self.app.register_task(ScheduledSequence())

        # ------------------ INSPECTOR ------------------ #

        self.inspect = self.app.control.inspect()
        self.ping()

    def post_run(self):
        self.spawn_daemon(
            worker=self.app.Worker(quiet=self.quiet).start,
            scheduler=self.app.Beat(socket_timeout=None, quiet=self.quiet).run,
        )

    ###################################################
    #              COMMON GETTER/SETTER               #
    ###################################################

    def get_by_task_id(self, task_id, wait=False, timeout=30):
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
            ret["result"] = task.get(timeout=timeout, disable_sync_subtasks=False)

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
        return self.queue.delay(wlk.jid, nd.jid, args).task_id

    ###################################################
    #                     CLEANER                     #
    ###################################################

    def failed(self):
        super().failed()
        self.terminate_daemon("worker", "scheduler")

    # ---------------- PROXY EVENTS ----------------- #

    def on_delete(self):
        self.terminate_daemon("worker", "scheduler")
