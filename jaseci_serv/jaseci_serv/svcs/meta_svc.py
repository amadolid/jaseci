from jaseci.svcs.meta_svc import meta_svc as ms
from jaseci_serv.svcs.redis.redis_svc import redis_svc
from jaseci_serv.svcs.task.task_svc import task_svc
from jaseci_serv.svcs.mail.mail_svc import mail_svc


class meta_svc(ms):
    def services(self, _hook):
        if _hook is None:
            _hook = self.hook()
        redis_svc(_hook)
        task_svc(_hook)
        mail_svc(_hook)

    def build_hook(self):
        from jaseci_serv.base.models import GlobalVars, JaseciObject
        from jaseci_serv.base.orm_hook import orm_hook

        return orm_hook(objects=JaseciObject.objects, globs=GlobalVars.objects)

    def build_master(self):
        from jaseci_serv.base.models import master

        return master(h=self.build_hook(), persist=False)
