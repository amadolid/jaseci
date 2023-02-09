"""Built in actions for Jaseci"""
from jaseci import JsOrc
from jaseci.actions.live_actions import jaseci_action
from jaseci.svc.task_svc import TaskService


@jaseci_action()
@JsOrc.inject(services=[("task", "task_svc")])  # will alias
def get_result(task_id, wait, meta, task_svc: TaskService = None):
    """
    Get task result by task_id
    """

    if not task_svc.is_running():
        raise Exception("Task hook is not yet initialized!")

    return task_svc.get_by_task_id(task_id, wait)
