from time import sleep

from kubernetes.client.rest import ApiException
from jaseci.utils.utils import logger
from jaseci.svc import CommonService, ServiceState as Ss
from jaseci.svc.kubernetes import Kube
from .common import JSORC_CONFIG, JsOrcProperties

#################################################
#                  JASECI ORC                   #
#################################################


class JsOrcService(CommonService, JsOrcProperties):

    ###################################################
    #                   INITIALIZER                   #
    ###################################################

    def __init__(self, hook=None):
        JsOrcProperties.__init__(self, __class__)
        CommonService.__init__(self, __class__, hook)

    ###################################################
    #                     BUILDER                     #
    ###################################################

    def build(self, hook=None):
        configs = self.get_config(hook)
        enabled = configs.pop("enabled", True)

        if enabled:
            self.quiet = configs.get("quiet", False)
            self.interval = configs.get("interval", 10)
            self.namespace = configs.get("namespace", "default")
            self.keep_alive = configs.get("keep_alive", [])

            self.app = JsOrc(hook.meta, hook.kube.app)
            self.state = Ss.RUNNING
            # self.app.check(self.namespace, "redis")
            self.spawn_daemon(jsorc=self.interval_check)
        else:
            self.state = Ss.DISABLED

    def interval_check(self):
        while True:
            sleep(self.interval)
            for svc in self.keep_alive:
                try:
                    self.app.check(self.namespace, svc)
                except Exception:
                    logger.exception("Skipping any issue!")

    ###################################################
    #                     CLEANER                     #
    ###################################################

    def reset(self, hook):
        self.terminate_daemon("jsorc")
        super().reset(hook)

    def failed(self):
        super().failed()
        self.terminate_daemon("jsorc")

    ####################################################
    #                    OVERRIDDEN                    #
    ####################################################

    def build_config(self, hook) -> dict:
        return hook.build_config("JSORC_CONFIG", JSORC_CONFIG)


# ----------------------------------------------- #


class JsOrc:
    def __init__(self, meta, kube: Kube):
        self.meta = meta
        self.kube = kube

    def read(self, api: str, name: str, namespace: str):
        try:
            return self.kube.read(api, name, namespace=namespace)
        except ApiException as e:
            logger.exception(
                f"Error retrieving {api} for `{name}` with namespace `{namespace}`"
            )
            return e

    def check(self, namespace, svc):

        svc = self.meta.get_service(svc)

        if not svc.is_running() and not (svc.kube is None):
            config_map = svc.kube
            pod_name = ""
            for kind, confs in config_map.items():
                for conf in confs:
                    name = conf["metadata"]["name"]
                    if kind == "Service":
                        pod_name = name
                    res = self.read(kind, name, namespace)
                    if hasattr(res, "status") and res.status == 404 and conf:
                        self.kube.create(kind, namespace, conf)

            if config_map:
                res = self.read("Endpoints", pod_name, namespace)
                if res.metadata:
                    svc.reset(self.meta.build_hook())
            else:
                svc.reset(self.meta.build_hook())
