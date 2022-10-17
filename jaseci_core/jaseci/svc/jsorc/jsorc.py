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

            self.app = JsOrc(hook.meta, hook.kube.app, self.quiet)
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
    def __init__(self, meta, kube: Kube, quiet: bool):
        self.meta = meta
        self.kube = kube
        self.quiet = quiet

    def is_running(self, name: str, namespace: str):
        try:
            return (
                self.kube.core.list_namespaced_pod(
                    namespace=namespace, label_selector=f"pod={name}"
                )
                .items[0]
                .status.phase
                == "Running"
            )
        except Exception:
            return False

    def create(self, kind: str, name: str, namespace: str, conf: dict):
        try:
            if not self.quiet:
                logger.info(
                    f"Creating {kind} for `{name}` with namespace `{namespace}`"
                )
            self.kube.create(kind, namespace, conf)
        except ApiException:
            if not self.quiet:
                logger.error(
                    f"Error creating {kind} for `{name}` with namespace `{namespace}`"
                )

    def read(self, kind: str, name: str, namespace: str):
        try:
            return self.kube.read(kind, name, namespace=namespace)
        except ApiException as e:
            if not self.quiet:
                logger.error(
                    f"Error retrieving {kind} for `{name}` with namespace `{namespace}`"
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
                        self.create(kind, name, namespace, conf)

            if config_map and self.is_running(pod_name, namespace):
                res = self.read("Endpoints", pod_name, namespace)
                if res.metadata:
                    svc.reset(self.meta.build_hook())
            else:
                svc.reset(self.meta.build_hook())
