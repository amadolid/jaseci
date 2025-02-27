import logging
from base64 import b64decode
from datetime import UTC, datetime
from os import getenv

from kubernetes import config
from kubernetes.client import (
    ApiClient,
    CoreV1Api,
    AppsV1Api,
    RbacAuthorizationV1Api,
    ApiextensionsV1Api,
    AdmissionregistrationV1Api,
    CustomObjectsApi,
)
from kubernetes.client.rest import ApiException

from .resolver import placeholder_resolver


if getenv("TEST_ENV") != "true":
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()


class KubernetesHelper:
    __cached_namespace__ = set()
    __no_namespace__ = [
        "Namespace",
        "ClusterRole",
        "ClusterRoleBinding",
        "CustomResourceDefinition",
        "ValidatingWebhookConfiguration",
    ]

    namespace = getenv("NAMESPACE", "default")
    app = ApiClient()
    core = CoreV1Api()
    api = AppsV1Api(app)
    api_ext = ApiextensionsV1Api(app)
    auth = RbacAuthorizationV1Api(app)
    reg_api = AdmissionregistrationV1Api(app)
    custom = CustomObjectsApi(app)

    assert app.call_api("/readyz", "GET")[1] == 200

    create_apis = {
        "Namespace": core.create_namespace,
        "Service": core.create_namespaced_service,
        "Deployment": api.create_namespaced_deployment,
        "ConfigMap": core.create_namespaced_config_map,
        "ServiceAccount": core.create_namespaced_service_account,
        "ClusterRole": auth.create_cluster_role,
        "ClusterRoleBinding": auth.create_cluster_role_binding,
        "Secret": core.create_namespaced_secret,
        "PersistentVolumeClaim": (core.create_namespaced_persistent_volume_claim),
        "DaemonSet": api.create_namespaced_daemon_set,
        "StatefulSet": api.create_namespaced_stateful_set,
        "CustomResourceDefinition": api_ext.create_custom_resource_definition,
        "ValidatingWebhookConfiguration": reg_api.create_validating_webhook_configuration,
        "Elasticsearch": lambda namespace, body: KubernetesHelper.custom.create_namespaced_custom_object(
            group="elasticsearch.k8s.elastic.co",
            version="v1",
            namespace=namespace,
            plural="elasticsearches",
            body=body,
        ),
        "Kibana": lambda namespace, body: KubernetesHelper.custom.create_namespaced_custom_object(
            group="kibana.k8s.elastic.co",
            version="v1",
            namespace=namespace,
            plural="kibanas",
            body=body,
        ),
        "Beat": lambda namespace, body: KubernetesHelper.custom.create_namespaced_custom_object(
            group="beat.k8s.elastic.co",
            version="v1beta1",
            namespace=namespace,
            plural="beats",
            body=body,
        ),
    }

    patch_apis = {
        "Namespace": core.patch_namespace,
        "Service": core.patch_namespaced_service,
        "Deployment": api.patch_namespaced_deployment,
        "ConfigMap": core.patch_namespaced_config_map,
        "ServiceAccount": core.patch_namespaced_service_account,
        "ClusterRole": auth.patch_cluster_role,
        "ClusterRoleBinding": auth.patch_cluster_role_binding,
        "Secret": core.patch_namespaced_secret,
        "PersistentVolumeClaim": (core.patch_namespaced_persistent_volume_claim),
        "DaemonSet": api.patch_namespaced_daemon_set,
        "StatefulSet": api.patch_namespaced_stateful_set,
        "CustomResourceDefinition": api_ext.patch_custom_resource_definition,
        "ValidatingWebhookConfiguration": reg_api.patch_validating_webhook_configuration,
        "Elasticsearch": lambda name, namespace, body: KubernetesHelper.custom.patch_namespaced_custom_object(
            group="elasticsearch.k8s.elastic.co",
            version="v1",
            namespace=namespace,
            plural="elasticsearches",
            name=name,
            body=body,
        ),
        "Kibana": lambda name, namespace, body: KubernetesHelper.custom.patch_namespaced_custom_object(
            group="kibana.k8s.elastic.co",
            version="v1",
            namespace=namespace,
            plural="kibanas",
            name=name,
            body=body,
        ),
        "Beat": lambda name, namespace, body: KubernetesHelper.custom.patch_namespaced_custom_object(
            group="beat.k8s.elastic.co",
            version="v1beta1",
            namespace=namespace,
            plural="beats",
            name=name,
            body=body,
        ),
    }

    delete_apis = {
        "Namespace": core.delete_namespace,
        "Service": core.delete_namespaced_service,
        "Deployment": api.delete_namespaced_deployment,
        "ConfigMap": core.delete_namespaced_config_map,
        "ServiceAccount": core.delete_namespaced_service_account,
        "ClusterRole": auth.delete_cluster_role,
        "ClusterRoleBinding": auth.delete_cluster_role_binding,
        "Secret": core.delete_namespaced_secret,
        "PersistentVolumeClaim": (core.delete_namespaced_persistent_volume_claim),
        "DaemonSet": api.delete_namespaced_daemon_set,
        "StatefulSet": api.delete_namespaced_stateful_set,
        "CustomResourceDefinition": api_ext.delete_custom_resource_definition,
        "ValidatingWebhookConfiguration": reg_api.delete_validating_webhook_configuration,
        "Elasticsearch": lambda name, namespace: KubernetesHelper.custom.delete_namespaced_custom_object(
            group="elasticsearch.k8s.elastic.co",
            version="v1",
            namespace=namespace,
            plural="elasticsearches",
            name=name,
        ),
        "Kibana": lambda name, namespace: KubernetesHelper.custom.delete_namespaced_custom_object(
            group="kibana.k8s.elastic.co",
            version="v1",
            namespace=namespace,
            plural="kibanas",
            name=name,
        ),
        "Beat": lambda name, namespace: KubernetesHelper.custom.delete_namespaced_custom_object(
            group="beat.k8s.elastic.co",
            version="v1beta1",
            namespace=namespace,
            plural="beats",
            name=name,
        ),
    }

    read_apis = {
        "Namespace": core.read_namespace,
        "Service": core.read_namespaced_service,
        "Endpoints": core.read_namespaced_endpoints,
        "Deployment": api.read_namespaced_deployment,
        "ConfigMap": core.read_namespaced_config_map,
        "ServiceAccount": core.read_namespaced_service_account,
        "ClusterRole": auth.read_cluster_role,
        "ClusterRoleBinding": auth.read_cluster_role_binding,
        "Secret": core.read_namespaced_secret,
        "PersistentVolumeClaim": core.read_namespaced_persistent_volume_claim,
        "DaemonSet": api.read_namespaced_daemon_set,
        "StatefulSet": api.read_namespaced_stateful_set,
        "CustomResourceDefinition": api_ext.read_custom_resource_definition,
        "ValidatingWebhookConfiguration": reg_api.read_validating_webhook_configuration,
        "Elasticsearch": lambda name, namespace: KubernetesHelper.custom.get_namespaced_custom_object(
            group="elasticsearch.k8s.elastic.co",
            version="v1",
            namespace=namespace,
            plural="elasticsearches",
            name=name,
        ),
        "Kibana": lambda name, namespace: KubernetesHelper.custom.get_namespaced_custom_object(
            group="kibana.k8s.elastic.co",
            version="v1",
            namespace=namespace,
            plural="kibanas",
            name=name,
        ),
        "Beat": lambda name, namespace: KubernetesHelper.custom.get_namespaced_custom_object(
            group="beat.k8s.elastic.co",
            version="v1beta1",
            namespace=namespace,
            plural="beats",
            name=name,
        ),
    }

    @classmethod
    def create(cls, kind: str, name: str, conf: dict, namespace: str):
        try:
            logging.info(f"Creating {kind} for `{name}` with namespace: `{namespace}`")
            if kind in cls.__no_namespace__:
                cls.create_apis[kind](body=conf)
            else:
                cls.create_apis[kind](namespace=namespace, body=conf)
        except ApiException as e:
            logging.error(
                f"Error creating {kind} for `{name}` with namespace: `{namespace}` -- {e}"
            )

    @classmethod
    def patch(cls, kind: str, name: str, conf: dict, namespace: str):
        try:
            logging.info(f"Patching {kind} for `{name}` with namespace: `{namespace}`")
            if kind in cls.__no_namespace__:
                cls.patch_apis[kind](name=name, body=conf)
            else:
                cls.patch_apis[kind](name=name, namespace=namespace, body=conf)
        except ApiException as e:
            logging.error(
                f"Error patching {kind} for `{name}` with namespace: `{namespace}` -- {e}"
            )

    @classmethod
    def read(cls, kind: str, name: str, namespace: str):
        try:
            logging.info(
                f"Retrieving {kind} for `{name}` with namespace: `{namespace}`"
            )
            if kind in cls.__no_namespace__:
                return cls.read_apis[kind](name=name)
            else:
                return cls.read_apis[kind](name=name, namespace=namespace)
        except ApiException as e:
            logging.error(
                f"Error retrieving {kind} for `{name}` with namespace: `{namespace}` -- {e}"
            )
            return e

    @classmethod
    def delete(cls, kind: str, name: str, namespace: str):
        try:
            logging.info(f"Deleting {kind} for `{name}` with namespace: `{namespace}`")
            if kind in cls.__no_namespace__:
                return cls.delete_apis[kind](name=name)
            else:
                return cls.delete_apis[kind](name=name, namespace=namespace)
        except ApiException as e:
            logging.error(
                f"Error deleting {kind} for `{name}` with namespace: `{namespace}` -- {e}"
            )
            return e

    @classmethod
    def apply(cls):
        pass

    @classmethod
    def is_pod_running(cls, name: str, namespace: str):
        try:
            return (
                cls.core.list_namespaced_pod(
                    namespace=namespace, label_selector=f"pod={name}"
                )
                .items[0]
                .status.phase
                == "Running"
            )
        except Exception:
            return False

    @classmethod
    def get_secret(cls, name: str, attr: str, namespace: str):
        try:
            return b64decode(
                cls.core.read_namespaced_secret(
                    name=name,
                    namespace=namespace,
                ).data[attr]
            ).decode()
        except Exception as e:
            logging.error(
                f"Error getting secret `{attr}` from `{name}` with namespace: `{namespace}` -- {e}"
            )
            return None

    @classmethod
    def resolve_manifest(cls, manifest: dict) -> dict:
        for kind, confs in manifest.items():
            if kind not in cls.__no_namespace__:
                for conf in confs.values():
                    metadata: dict = conf["metadata"]
                    namespace = metadata.get("namespace", "default")

                    if namespace and namespace not in cls.__cached_namespace__:
                        res = cls.read("Namespace", namespace, None)
                        if hasattr(res, "status") and res.status == 404:
                            cls.create(
                                "Namespace",
                                namespace,
                                {
                                    "apiVersion": "v1",
                                    "kind": "Namespace",
                                    "metadata": {
                                        "name": namespace,
                                        "labels": {"name": namespace},
                                    },
                                },
                                None,
                            )
                            # don't add it on cache since create is possible to fail
                        elif (
                            isinstance(res, dict) and "metadata" in res
                        ) or res.metadata:
                            cls.__cached_namespace__.add(namespace)

        placeholder_resolver(manifest, manifest)

        return manifest

    @classmethod
    def has_replicas(cls):
        try:
            return cls.read("Deployment", "jaseci", cls.namespace).spec.replicas > 1
        except Exception as e:
            logging.error(f"Error checking jaseci replica -- {e}")

    @classmethod
    def restart(cls):
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
            logging.error(f"Error triggering jaseci rollout restart -- {e}")
