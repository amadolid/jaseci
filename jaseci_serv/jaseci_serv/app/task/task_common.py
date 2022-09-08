from jaseci_serv.app.task.task_app import task_app
from celery import Task
from jaseci_serv.base.models import GlobalVars, JaseciObject


class queue(Task):
    def run(self, queue_id):
        from jaseci_serv.base.orm_hook import orm_hook

        ret = task_app.consume_queue(
            queue_id, orm_hook(objects=JaseciObject.objects, globs=GlobalVars.objects)
        )

        return ret
