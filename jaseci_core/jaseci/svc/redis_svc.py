from jaseci import JsOrc
from redis import Redis
from .common_svc import CommonService


@JsOrc.service(
    name="redis",
    config="REDIS_CONFIG",
    manifest="REDIS_MANIFEST",
    priority=0,
    proxy=True,
)
class RedisService(CommonService):
    # extending CommonService is not required as service will always extends CommonService

    def run(self):
        self.app = Redis(**self.config, decode_responses=True)
        self.app.ping()

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

    # ---------------- PROXY EVENTS ----------------- #

    def on_delete(self):
        if self.is_running():
            self.app.close()
