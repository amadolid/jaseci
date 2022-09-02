"""
Queue api functions as a mixin
"""
from jaseci.api.interface import interface


class queue_api:
    """
    Queue APIs

    APIs used for celery configuration and monitoring
    """

    @interface.private_api(allowed_methods=["get"])
    def queue(self, task_id: str = ""):
        """
        Monitor Queues
        """
        if not self._h.task_hook_ready():
            return "Task hook is not yet initialized!"

        if not task_id:
            return self._h.inspect_tasks()
        else:
            return self._h.get_by_task_id(task_id)

    @interface.admin_api()
    def task_reset(self):
        """
        Reinitialize celery to the current configs
        """
        self._h.task_reset()
