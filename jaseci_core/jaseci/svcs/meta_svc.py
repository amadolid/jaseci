from jaseci.svcs.common_svc import common_svc
from jaseci.svcs.redis.redis_svc import redis_svc
from jaseci.svcs.task.task_svc import task_svc
from jaseci.svcs.mail.mail_svc import mail_svc
from jaseci.utils.app_state import AppState as AS


class meta_svc(common_svc):
    def __init__(self, hook=None):
        super().__init__(meta_svc)

        if self.is_ready():
            self.state = AS.RUNNING
            self.app = {
                "hook": self.build_hook,
                "master": self.build_master,
            }

        self.services(hook)

    def services(self, _hook):
        if _hook is None:
            _hook = self.hook()
        redis_svc(_hook)
        task_svc(_hook)
        mail_svc(_hook)

    def hook(self):
        return self.app["hook"]()

    def master(self):
        return self.app["master"]()

    def build_hook(self):
        from jaseci.utils.redis_hook import redis_hook

        return redis_hook()

    def build_master(self):
        from jaseci.element.master import master

        return master(h=self.build_hook(), persist=False)
