import signal
import sys
from multiprocessing import Manager, Process
from uuid import UUID, uuid4

from ..utils.utils import logger
from .tasks import queue, schedule_queue
from celery import Celery
from redis import Redis

################################################
# ----------------- DEFAULTS ----------------- #
################################################

QUIET = True
PREFIX = "celery-task-meta-"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 1
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
CELERY_DEFAULT_CONFIGS = {
    "broker_url": REDIS_URL,
    "result_backend": REDIS_URL,
    "broker_connection_retry_on_startup": True,
    "task_track_started": True,
}

#################################################
# ----------------- TASK HOOK ----------------- #
#################################################


class task_hook:

    app = None
    inspect = None
    worker = None
    scheduler = None
    # -1 Failed : 0 Not Started : 1 Running
    state = 0
    quiet = False

    # ----------------- REGISTERED TASK ----------------- #
    queue = None
    schedule_queue = None

    # ----------------- DATA SOURCE ----------------- #
    main_hook = None
    shared_mem = None
    redis = None

    def __init__(self):

        self.allowed_scheduler = True

        if task_hook.state != -1 and task_hook.app is None:

            task_hook.main_hook = self

            try:
                self.__celery()

                if task_hook.inspect.ping() is None:
                    self.__tasks()
                    self.__worker()
                    if self.allowed_scheduler:
                        self.__scheduler()
                    task_hook.state = 1
            except Exception as e:
                task_hook.state = -1
                if not (task_hook.quiet):
                    logger.error(f"Celery initialization failed! Error: '{e}'")
                task_hook.app = None
                task_hook.terminate_worker()
                task_hook.terminate_scheduler()

    #################################################
    # ---------------- INITIALIZER ---------------- #
    #################################################

    def __celery(self):
        task_hook.app = Celery("celery")
        self.celery_config()
        task_hook.inspect = task_hook.app.control.inspect()
        task_hook.shared_mem = Manager().dict()

    def __worker(self):
        task_hook.worker = Process(
            target=task_hook.app.Worker(quiet=task_hook.quiet).start
        )
        task_hook.worker.daemon = True
        task_hook.worker.start()

    def __scheduler(self):
        task_hook.scheduler = Process(
            target=task_hook.app.Beat(quiet=task_hook.quiet).run
        )
        task_hook.scheduler.daemon = True
        task_hook.scheduler.start()

    def __tasks(self):
        task_hook.queue = task_hook.app.register_task(queue())
        task_hook.schedule_queue = task_hook.app.register_task(schedule_queue())

    ##########################################################
    # ---------------- COMMON GETTER/SETTER ---------------- #
    ##########################################################

    def task_app(self):
        return task_hook.app

    def task_hook_ready(self):
        return task_hook.state == 1 and not (task_hook.app is None)

    def task_quiet(self, quiet=QUIET):
        task_hook.quiet = quiet

    # ---------------- QUEUE RELATED ---------------- #

    def inspect_tasks(self):
        return {
            "scheduled": task_hook.inspect.scheduled(),
            "active": task_hook.inspect.active(),
            "reserved": task_hook.inspect.reserved(),
        }

    # ORM_HOOK OVERRIDE
    def get_by_task_id(self, task_id):
        ret = {"status": "NOT_STARTED"}
        task = task_hook.redis.get(f"{PREFIX}{task_id}")
        if task and "status" in task:
            ret["status"] = task["status"]
            if ret["status"] == "SUCESS":
                ret["result"] = task["result"]
        return ret

    #############################################
    # ---------------- QUEUING ---------------- #
    #############################################

    def get_element(jid):
        from ..actor.walker import walker

        if not (task_hook.redis is None) and jid in task_hook.shared_mem:
            kwargs = task_hook.shared_mem.pop(jid)
            namespaces = kwargs.pop("namespaces")
            wlk = walker(h=task_hook.main_hook, **kwargs)
            wlk.namespaces = namespaces
            return wlk
        else:
            return task_hook.main_hook.get_obj("bypass", UUID(jid), True)

    def add_queue(self, wlk):
        queue_id = str(uuid4())

        if not (task_hook.redis is None):
            jid, meta = wlk.dismantle()
            task_hook.shared_mem.update({jid: meta})

        task_hook.shared_mem.update(
            {queue_id: {"wlk": wlk.jid, "proc": wlk._async_procedure}}
        )
        return task_hook.queue.delay(queue_id).task_id

    def consume_queue(queue_id):
        que = task_hook.shared_mem.pop(queue_id)
        wlk = task_hook.get_element(que["wlk"])

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

    #############################################
    # ---------------- CLEANER ---------------- #
    #############################################

    def terminate_worker():
        if not (task_hook.worker is None):
            if not (task_hook.quiet):
                logger.warn("Terminating task worker ...")
            task_hook.worker.terminate()
            task_hook.worker = None

    def terminate_scheduler():
        if not (task_hook.scheduler is None):
            if not (task_hook.quiet):
                logger.warn("Terminating task scheduler ...")
            task_hook.scheduler.terminate()
            task_hook.scheduler = None

    ############################################
    # ---------------- CONFIG ---------------- #
    ############################################

    # ORM_HOOK OVERRIDE
    def celery_config(self):
        """Add celery config"""
        self.allowed_scheduler = False
        task_hook.app.conf.update(**CELERY_DEFAULT_CONFIGS)
        task_hook.redis = Redis(host=REDIS_HOST, db=REDIS_DB, decode_responses=True)
        task_hook.quiet = QUIET


# --------------------------------------------- #

#######################################################
# ----------------- PROCESS CLEANER ----------------- #
#######################################################

EXITING = False


def terminate_gracefully(sig, frame):
    global EXITING

    if not EXITING:
        EXITING = True
        task_hook.terminate_worker()
        task_hook.terminate_scheduler()
        logger.warn("Exitting gracefully ...")
        sys.exit(0)


signal.signal(signal.SIGINT, terminate_gracefully)
