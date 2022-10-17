from jaseci.svc import KubernetesService as Ks
from jaseci_serv.jaseci_serv.configs import KUBE_CONFIG


class KubernetesService(Ks):
    def build_config(self, hook) -> dict:
        return hook.build_config("KUBE_CONFIG", KUBE_CONFIG)
