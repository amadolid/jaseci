from jaseci.svc import RedisService as Rs
from jaseci_serv.jaseci_serv.configs import REDIS_CONFIG


class RedisService(Rs):
    def build_config(self, hook) -> dict:
        return hook.build_config("REDIS_CONFIG", REDIS_CONFIG)
