import six
from jaseci import JsOrc

from kubernetes import config as kubernetes_config
from kubernetes.client import (
    ApiClient,
    CoreV1Api,
    AppsV1Api,
    RbacAuthorizationV1Api,
    ApiextensionsV1Api,
    AdmissionregistrationV1Api,
)
from kubernetes.client.exceptions import ApiTypeError, ApiValueError
from kubernetes.client.rest import ApiException

from jaseci.utils.utils import logger


@JsOrc.service(name="kube", config="KUBE_CONFIG")
class KubeService(JsOrc.CommonService):
    ###################################################
    #                     BUILDER                     #
    ###################################################

    _no_namespace = [
        "Namespace",
        "ClusterRole",
        "ClusterRoleBinding",
        "CustomResourceDefinition",
        "ValidatingWebhookConfiguration",
    ]

    def run(self):
        self._in_cluster = self.config.get("in_cluster", True)
        if self._in_cluster:
            kubernetes_config.load_incluster_config()
        else:
            kubernetes_config.load_kube_config()

        self.namespace = self.config.get("namespace", "default")
        config = self.config.get("config")

        self.app = ApiClient(config)
        self.core = CoreV1Api(config)
        self.api = AppsV1Api(self.app)
        self.api_ext = ApiextensionsV1Api(self.app)
        self.auth = RbacAuthorizationV1Api(self.app)
        self.reg_api = AdmissionregistrationV1Api(self.app)

        self.ping()
        self.defaults()

    def defaults(self):
        self.create_apis = {
            "Namespace": self.core.create_namespace,
            "Service": self.core.create_namespaced_service,
            "Deployment": self.api.create_namespaced_deployment,
            "ConfigMap": self.core.create_namespaced_config_map,
            "ServiceAccount": self.core.create_namespaced_service_account,
            "ClusterRole": self.auth.create_cluster_role,
            "ClusterRoleBinding": self.auth.create_cluster_role_binding,
            "Secret": self.core.create_namespaced_secret,
            "PersistentVolumeClaim": (
                self.core.create_namespaced_persistent_volume_claim
            ),
            "DaemonSet": self.api.create_namespaced_daemon_set,
            "StatefulSet": self.api.create_namespaced_stateful_set,
            "CustomResourceDefinition": self.api_ext.create_custom_resource_definition,
            "ValidatingWebhookConfiguration": self.reg_api.create_validating_webhook_configuration,
            "Elasticsearch": self.custom_create,
        }
        self.patch_apis = {
            "Namespace": self.core.patch_namespace,
            "Service": self.core.patch_namespaced_service,
            "Deployment": self.api.patch_namespaced_deployment,
            "ConfigMap": self.core.patch_namespaced_config_map,
            "ServiceAccount": self.core.patch_namespaced_service_account,
            "ClusterRole": self.auth.patch_cluster_role,
            "ClusterRoleBinding": self.auth.patch_cluster_role_binding,
            "Secret": self.core.patch_namespaced_secret,
            "PersistentVolumeClaim": (
                self.core.patch_namespaced_persistent_volume_claim
            ),
            "DaemonSet": self.api.patch_namespaced_daemon_set,
            "StatefulSet": self.api.patch_namespaced_stateful_set,
            "CustomResourceDefinition": self.api_ext.patch_custom_resource_definition,
            "ValidatingWebhookConfiguration": self.reg_api.patch_validating_webhook_configuration,
        }
        self.delete_apis = {
            "Namespace": self.core.delete_namespace,
            "Service": self.core.delete_namespaced_service,
            "Deployment": self.api.delete_namespaced_deployment,
            "ConfigMap": self.core.delete_namespaced_config_map,
            "ServiceAccount": self.core.delete_namespaced_service_account,
            "ClusterRole": self.auth.delete_cluster_role,
            "ClusterRoleBinding": self.auth.delete_cluster_role_binding,
            "Secret": self.core.delete_namespaced_secret,
            "PersistentVolumeClaim": (
                self.core.delete_namespaced_persistent_volume_claim
            ),
            "DaemonSet": self.api.delete_namespaced_daemon_set,
            "StatefulSet": self.api.delete_namespaced_stateful_set,
            "CustomResourceDefinition": self.api_ext.delete_custom_resource_definition,
            "ValidatingWebhookConfiguration": self.reg_api.delete_validating_webhook_configuration,
        }
        self.read_apis = {
            "Namespace": self.core.read_namespace,
            "Service": self.core.read_namespaced_service,
            "Endpoints": self.core.read_namespaced_endpoints,
            "Deployment": self.api.read_namespaced_deployment,
            "ConfigMap": self.core.read_namespaced_config_map,
            "ServiceAccount": self.core.read_namespaced_service_account,
            "ClusterRole": self.auth.read_cluster_role,
            "ClusterRoleBinding": self.auth.read_cluster_role_binding,
            "Secret": self.core.read_namespaced_secret,
            "PersistentVolumeClaim": self.core.read_namespaced_persistent_volume_claim,
            "DaemonSet": self.api.read_namespaced_daemon_set,
            "StatefulSet": self.api.read_namespaced_stateful_set,
            "CustomResourceDefinition": self.api_ext.read_custom_resource_definition,
            "ValidatingWebhookConfiguration": self.reg_api.read_validating_webhook_configuration,
        }

    ###################################################
    #                     COMMONS                     #
    ###################################################

    def ping(self):
        res = self.app.call_api("/readyz", "GET")
        return res[1] == 200

    def in_cluster(self):
        """
        Check if JSORC/Jaseci is running in a kubernetes cluster
        """
        try:
            return self._in_cluster and self.ping()
        except ApiException as e:
            logger.info(f"Kubernetes cluster environment check failed: {e}")
            return False

    def resolve_namespace(self, conf: dict, namespace: str = None):
        return conf.get("metadata", {}).get("namespace") or namespace or self.namespace

    def create(
        self,
        kind: str,
        name: str,
        conf: dict,
        namespace: str = None,
        log_pref: str = "",
    ):
        namespace = self.resolve_namespace(conf, namespace)
        try:
            logger.info(
                f"{log_pref} Creating {kind} for `{name}` with namespace `{namespace}`"
            )
            if kind in self._no_namespace:
                self.create_apis[kind](body=conf)
            else:
                self.create_apis[kind](namespace=namespace, body=conf)
        except ApiException as e:
            logger.error(
                f"{log_pref} Error creating {kind} for `{name}` with namespace `{namespace}` -- {e}"
            )

    def patch(
        self,
        kind: str,
        name: str,
        conf: dict,
        namespace: str = None,
        log_pref: str = "",
    ):
        namespace = self.resolve_namespace(conf, namespace)
        try:
            logger.info(
                f"{log_pref} Patching {kind} for `{name}` with namespace `{namespace}`"
            )
            if kind in self._no_namespace:
                self.patch_apis[kind](name=name, body=conf)
            else:
                self.patch_apis[kind](name=name, namespace=namespace, body=conf)
        except ApiException as e:
            logger.error(
                f"{log_pref} Error patching {kind} for `{name}` with namespace `{namespace}` -- {e}"
            )

    def read(self, kind: str, name: str, namespace: str = None, log_pref: str = ""):
        namespace = namespace or self.namespace
        try:
            logger.info(
                f"{log_pref} Retrieving {kind} for `{name}` with namespace `{namespace}`"
            )
            if kind in self._no_namespace:
                return self.read_apis[kind](name=name)
            else:
                return self.read_apis[kind](name=name, namespace=namespace)
        except ApiException as e:
            logger.error(
                f"{log_pref} Error retrieving {kind} for `{name}` with namespace `{namespace}` -- {e}"
            )
            return e

    def delete(self, kind: str, name: str, namespace: str = None, log_pref: str = ""):
        namespace = namespace or self.namespace
        try:
            logger.info(
                f"{log_pref} Deleting {kind} for `{name}` with namespace `{namespace}`"
            )
            if kind in self._no_namespace:
                return self.delete_apis[kind](name=name)
            else:
                return self.delete_apis[kind](name=name, namespace=namespace)
        except ApiException as e:
            logger.error(
                f"{log_pref} Error deleting {kind} for `{name}` with namespace `{namespace}` -- {e}"
            )
            return e

    def is_pod_running(self, name: str, namespace: str = None):
        namespace = namespace or self.namespace
        try:
            return (
                self.core.list_namespaced_pod(
                    namespace=namespace, label_selector=f"pod={name}"
                )
                .items[0]
                .status.phase
                == "Running"
            )
        except Exception:
            return False

    def terminate_jaseci(self, name: str, namespace: str = None) -> bool:
        namespace = namespace or self.namespace
        try:
            for item in self.core.list_namespaced_pod(
                namespace=namespace, label_selector=f"pod={name}"
            ).items:
                self.core.delete_namespaced_pod(item.metadata.name, namespace)
                raise SystemExit("Force termination to restart the pod!")
        except Exception:
            return False

    def custom_create(self, namespace, body, **kwargs):
        kwargs["_return_http_data_only"] = True

        local_var_params = locals()

        all_params = ["body", "pretty", "dry_run", "field_manager", "field_validation"]
        all_params.extend(
            [
                "async_req",
                "_return_http_data_only",
                "_preload_content",
                "_request_timeout",
            ]
        )

        for key, val in six.iteritems(local_var_params["kwargs"]):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method create_custom_resource_definition" % key
                )
            local_var_params[key] = val
        del local_var_params["kwargs"]
        # verify the required parameter 'body' is set
        if self.app.client_side_validation and (
            "body" not in local_var_params
            or local_var_params["body"] is None  # noqa: E501
        ):  # noqa: E501
            raise ApiValueError(
                "Missing the required parameter `body` when calling `create_custom_resource_definition`"
            )  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []
        if (
            "pretty" in local_var_params and local_var_params["pretty"] is not None
        ):  # noqa: E501
            query_params.append(("pretty", local_var_params["pretty"]))  # noqa: E501
        if (
            "dry_run" in local_var_params and local_var_params["dry_run"] is not None
        ):  # noqa: E501
            query_params.append(("dryRun", local_var_params["dry_run"]))  # noqa: E501
        if (
            "field_manager" in local_var_params
            and local_var_params["field_manager"] is not None
        ):  # noqa: E501
            query_params.append(
                ("fieldManager", local_var_params["field_manager"])
            )  # noqa: E501
        if (
            "field_validation" in local_var_params
            and local_var_params["field_validation"] is not None
        ):  # noqa: E501
            query_params.append(
                ("fieldValidation", local_var_params["field_validation"])
            )  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if "body" in local_var_params:
            body_params = local_var_params["body"]
        # HTTP header `Accept`
        header_params["Accept"] = self.app.select_header_accept(
            [
                "application/json",
                "application/yaml",
                "application/vnd.kubernetes.protobuf",
            ]
        )  # noqa: E501

        # Authentication setting
        auth_settings = ["BearerToken"]  # noqa: E501

        return self.app.call_api(
            "/apis/elasticsearch.k8s.elastic.co/v1/elasticsearches",
            "POST",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=None,
            auth_settings=auth_settings,
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get(
                "_return_http_data_only"
            ),  # noqa: E501
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats=collection_formats,
        )
