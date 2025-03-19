"""Kubenertes Services."""

from base64 import b64decode, b64encode
from datetime import UTC, datetime
from os import getenv

from kubernetes import config
from kubernetes.client import ApiClient, AppsV1Api, CoreV1Api
from kubernetes.client.rest import ApiException

from orjson import dumps, loads

from ..dtos.deployment import Deployment, ModulesType
from ..utils import logger


class KubernetesService:
    """Kubernetes Service."""

    try:
        config.load_incluster_config()
        in_cluser = True
    except config.ConfigException:
        in_cluser = False
        config.load_kube_config()

    namespace = getenv("NAMESPACE", "default")
    app = ApiClient()
    core = CoreV1Api()
    api = AppsV1Api(app)

    assert app.call_api("/readyz", "GET")[1] == 200

    @classmethod
    def get_modules(cls) -> ModulesType:
        """Get modules."""
        try:
            return loads(
                b64decode(
                    cls.core.read_namespaced_secret(
                        name="jac-orc",
                        namespace=cls.namespace,
                    ).data["MODULES"]
                )
            )
        except Exception:
            logger.exception(f"Error getting modules with namespace: `{cls.namespace}`")
            return {}

    @classmethod
    def update_modules(cls, deployment: Deployment) -> None:
        """Update modules."""
        if cls.in_cluser:
            modules = cls.get_modules()

            namespace: str = deployment.config["namespace"]
            if not (target_namespace := modules.get(namespace)):
                target_namespace = modules[namespace] = {}

            module: str = deployment.module
            if not (target_module := target_namespace.get(module)):
                target_module = target_namespace[module] = {}

            target_module[deployment.config["name"]] = deployment.config

            try:
                cls.core.patch_namespaced_secret(
                    name="jac-orc",
                    namespace=cls.namespace,
                    body={"data": {"MODULES": b64encode(dumps(modules))}},
                )
            except Exception:
                logger.exception(
                    f"Error updating modules with request: `{deployment.model_dump_json()}`"
                )

    @classmethod
    def restart(cls) -> None:
        """Restart Service."""
        try:
            return cls.api.patch_namespaced_deployment(
                name="jaseci",
                namespace=cls.namespace,
                body={
                    "spec": {
                        "template": {
                            "metadata": {
                                "annotations": {
                                    "kubectl.kubernetes.io/restartedAt": datetime.now(
                                        UTC
                                    ).isoformat("T")
                                    + "Z"
                                }
                            }
                        }
                    }
                },
            )
        except ApiException as e:
            logger.error(f"Error triggering jaseci rollout restart -- {e}")
