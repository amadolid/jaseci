from json import dumps, loads
from redis import Redis

from jaseci.svc import CommonService, ServiceState as Ss
from .config import REDIS_CONFIG
from .kube import REDIS_KUBE


#################################################
#                  REDIS HOOK                   #
#################################################


class RedisService(CommonService):

    ###################################################
    #                   INITIALIZER                   #
    ###################################################

    def __init__(self, hook=None):
        super().__init__(hook)

    ###################################################
    #                     BUILDER                     #
    ###################################################

    def builder(self, hook=None):
        configs = self.build_settings(hook)
        enabled = configs.pop("enabled", True)

        if enabled:
            self.quiet = configs.pop("quiet", False)
            self.app = Redis(**configs, decode_responses=True)
            self.app.ping()
            self.state = Ss.RUNNING
        else:
            self.state = Ss.DISABLED

    ###################################################
    #                     COMMONS                     #
    ###################################################

    def get(self, name):
        return self.app.get(name)

    def set(self, name, val):
        self.app.set(name, val)

    def exists(self, name):
        return self.app.exists(name)

    def delete(self, name):
        self.app.delete(name)

    def hget(self, name, key):
        return self.app.hget(name, key)

    def hset(self, name, key, val):
        self.app.hset(name, key, val)

    def hexists(self, name, key):
        return self.app.hexists(name, key)

    def hdel(self, name, key):
        self.app.hdel(name, key)

    def hkeys(self, name):
        return self.app.hkeys(name)

    ###################################################
    #                     CLEANER                     #
    ###################################################

    def clear(self):
        if self.is_running():
            self.app.flushdb()

    ###################################################
    #                     CONFIG                      #
    ###################################################

    def build_config(self, hook) -> dict:
        return hook.service_glob("REDIS_CONFIG", REDIS_CONFIG)

    def build_kube(self, hook) -> dict:
        return hook.service_glob("REDIS_KUBE", REDIS_KUBE)


# ----------------------------------------------- #
