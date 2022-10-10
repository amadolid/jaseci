from jaseci.svc import PromotheusService as Ps
from jaseci_serv.jaseci_serv.configs import PROMON_CONFIG


class PromotheusService(Ps):
    def build_config(self, hook) -> dict:
        return hook.build_config("PROMON_CONFIG", PROMON_CONFIG)
