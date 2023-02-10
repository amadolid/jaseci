from copy import deepcopy

from kubernetes import config as kubernetes_config
from kubernetes.client import ApiClient, CoreV1Api, AppsV1Api, RbacAuthorizationV1Api
from kubernetes.client.rest import ApiException

from jaseci.utils.utils import logger
from jaseci.actions.live_actions import load_action_config
from jaseci.svc.actions_optimizer.actions_optimizer import ActionsOptimizer

import time
import numpy as np


class JsOrcAutomation:
    def __init__(self):
        from jaseci import JsOrc

        self.jsorc = JsOrc
        self.enabled = False
        self.benchmark = {
            "jsorc": {"active": False, "requests": {}},
            "actions_optimizer": {"active": False, "requests": {}},
        }
        self.actions_history = {"active": False, "history": []}
        self.actions_calls = {}
        self.system_states = {"active": False, "states": []}
        self.actions_optimizer = ActionsOptimizer(
            benchmark=self.benchmark["actions_optimizer"],
            actions_history=self.actions_history,
            actions_calls=self.actions_calls,
        )

    ###################################################
    #                     BUILDER                     #
    ###################################################

    # def build(self):
    #     try:
    #         hook = self.build_context("hook")
    #         config = hook.service_glob("META_CONFIG", META_CONFIG)
    #         if config.pop("automation", False):
    #             self.kubernetes = Kube(**config.pop("kubernetes", KUBERNETES_CONFIG))
    #             self.actions_optimizer.kube = self.kubernetes
    #             self.prometheus = self.meta.get_service("promon", hook)
    #             self.backoff_interval = config.pop("backoff_interval", 10)
    #             self.namespace = config.pop("namespace", "default")
    #             self.actions_optimizer.namespace = self.namespace
    #             self.keep_alive = config.pop(
    #                 "keep_alive", ["promon", "redis", "task", "mail"]
    #             )
    #             self.enabled = True
    #         else:
    #             self.enabled = False
    #     except Exception:
    #         self.enabled = False

    def interval_check(self):
        hook = self.meta.build_hook()
        for svc in self.keep_alive:
            try:
                self.check(self.namespace, svc, hook)
            except Exception as e:
                logger.exception(
                    f"Error checking {svc} !\n" f"{e.__class__.__name__}: {e}"
                )
        self.optimize(jsorc_interval=self.backoff_interval)
        self.record_system_state()

    ###################################################
    #                   KUBERNETES                    #
    ###################################################

    def in_cluster(self):
        """
        Check if JSORC/Jaseci is running in a kubernetes cluster
        """
        try:
            if not hasattr(self, "kubernetes"):
                return False
            return self.kubernetes.ping()
        except ApiException as e:
            logger.info(f"Kubernetes cluster environment check failed: {e}")
            return False

    def create(self, kind: str, name: str, namespace: str, conf: dict):
        try:
            logger.info(f"Creating {kind} for `{name}` with namespace `{namespace}`")
            self.kubernetes.create(kind, namespace, conf)
        except ApiException as e:
            logger.error(
                f"Error creating {kind} for `{name}` with namespace `{namespace}` -- {e}"
            )

    def patch(self, kind: str, name: str, namespace: str, conf: dict):
        try:
            logger.info(f"Patching {kind} for `{name}` with namespace `{namespace}`")
            self.kubernetes.patch(kind, name, namespace, conf)
        except ApiException as e:
            logger.error(
                f"Error patching {kind} for `{name}` with namespace `{namespace}` -- {e}"
            )

    def read(self, kind: str, name: str, namespace: str):
        try:
            logger.info(f"Retrieving {kind} for `{name}` with namespace `{namespace}`")
            return self.kubernetes.read(kind, name, namespace=namespace)
        except ApiException as e:
            logger.error(
                f"Error retrieving {kind} for `{name}` with namespace `{namespace}` -- {e}"
            )
            return e

    def delete(self, kind: str, name: str, namespace: str):
        try:
            logger.info(f"Deleting {kind} for `{name}` with namespace `{namespace}`")
            return self.kubernetes.delete(kind, name, namespace=namespace)
        except ApiException as e:
            logger.error(
                f"Error deleting {kind} for `{name}` with namespace `{namespace}` -- {e}"
            )
            return e

    ###################################################
    #                 ACTION MANAGER                  #
    ###################################################
    def load_action_config(self, config, name):
        """
        Load the config for an action
        """
        return load_action_config(config, name)

    def load_actions(self, name, mode):
        """
        Load an action as local, module or remote.
        """
        # Using module for local
        mode = "module" if mode == "local" else mode

        if mode == "module":
            self.actions_optimizer.load_action_module(name)
        elif mode == "remote":
            self.actions_optimizer.load_action_remote(name)

    def unload_actions(self, name, mode, retire_svc):
        """
        Unload an action
        """
        # We are using module for local
        mode = "module" if mode == "local" else mode
        if mode == "auto":
            res = self.actions_optimizer.unload_action_auto(name)
            if not res[0]:
                return res
            if retire_svc:
                self.retire_uservice(name)
            return res
        elif mode == "module":
            return self.actions_optimizer.unload_action_module(name)
        elif mode == "remote":
            res = self.actions_optimizer.unload_action_remote(name)
            if not res[0]:
                return res
            if retire_svc:
                self.retire_uservice(name)
            return res
        else:
            return (False, f"Unrecognized action mode {mode}.")

    def retire_uservice(self, name):
        """
        Retire a remote microservice for the action.
        """
        self.actions_optimizer.retire_remote(name)

    def get_actions_status(self, name=""):
        """
        Return the status of the action
        """
        return self.actions_optimizer.get_actions_status(name)

    def actions_tracking_start(self):
        """ """
        self.actions_history["active"] = True
        self.actions_history["history"] = [{"ts": time.time()}]
        self.actions_calls.clear()

    def actions_tracking_stop(self):
        """ """
        if not self.actions_history["active"]:
            return []

        self.actions_optimizer.summarize_action_calls()

        return self.actions_history["history"]

    def benchmark_start(self):
        """
        Put JSORC under benchmark mode.
        """
        self.benchmark["jsorc"]["active"] = True
        self.benchmark["jsorc"]["requests"] = {}
        self.benchmark["jsorc"]["start_ts"] = time.time()

    def state_tracking_start(self):
        """
        Ask JSORC to start tracking the state of the system as observed by JSORC on every interval.
        """
        self.system_states = {"active": True, "states": []}

    def state_tracking_stop(self):
        """
        Stop state tracking for JSORC
        """
        ret = self.system_states
        self.system_states = {"active": True, "states": []}
        return ret

    def state_tracking_report(self):
        """
        Return state tracking history so far
        """
        return self.system_states

    def record_system_state(self):
        """
        Record system state
        """
        if self.system_states["active"]:
            ts = int(time.time())
            prom_profile = self.prometheus.info(
                namespace=self.namespace,
                exclude_prom=True,
                timestamp=ts,
                duration=self.backoff_interval,
            )
            self.system_states["states"].append(
                {
                    "ts": ts,
                    "actions": self.get_actions_status(name=""),
                    "prometheus": prom_profile,
                }
            )

    def benchmark_stop(self, report):
        """
        Stop benchmark mode and report result during the benchmark period
        """
        if not self.benchmark["jsorc"]["active"]:
            return {}

        res = self.benchmark_report()
        self.benchmark["jsorc"]["requests"] = {}
        self.benchmark["jsorc"]["active"] = False

        if report:
            return res
        else:
            return {}

    def benchmark_report(self):
        """
        Summarize benchmark results and report.
        """
        summary = {}
        duration = time.time() - self.benchmark["jsorc"]["start_ts"]
        for request, data in self.benchmark["jsorc"]["requests"].items():
            summary[request] = {}
            all_reqs = []
            for req_name, times in data.items():
                if len(times) == 0:
                    continue
                all_reqs.extend(times)
                summary[request][req_name] = {
                    "throughput": len(times) / duration,
                    "average_latency": sum(times) / len(times) * 1000,
                    "50th_latency": np.percentile(times, 50) * 1000,
                    "90th_latency": np.percentile(times, 90) * 1000,
                    "95th_latency": np.percentile(times, 95) * 1000,
                    "99th_latency": np.percentile(times, 99) * 1000,
                }
            summary[request]["all"] = {
                "throughput": len(all_reqs) / duration,
                "average_latency": sum(all_reqs) / len(all_reqs) * 1000,
                "50th_latency": np.percentile(all_reqs, 50) * 1000,
                "90th_latency": np.percentile(all_reqs, 90) * 1000,
                "95th_latency": np.percentile(all_reqs, 95) * 1000,
                "99th_latency": np.percentile(all_reqs, 99) * 1000,
            }

        return summary

    def record_state(self):
        """
        Record the current state of the system observed by JSORC
        """

    def add_to_benchmark(self, request_type, request, request_time):
        """
        Add requests to benchmark performance tracking
        """
        for bm in self.benchmark.values():
            if request_type not in bm["requests"]:
                bm["requests"][request_type] = {"_default_": []}
            if request_type == "walker_run":
                walker_name = dict(request.data)["name"]
                if walker_name not in bm["requests"][request_type]:
                    bm["requests"][request_type][walker_name] = []
                bm["requests"][request_type][walker_name].append(request_time)
            else:
                bm["requests"][request_type]["_default_"].append(request_time)

    def set_action_policy(self, policy_name, policy_params):
        """
        Set an action optimizer policy
        """
        return self.actions_optimizer.set_action_policy(policy_name, policy_params)

    def get_action_policy(self):
        """
        Get the current action optimization policy
        """
        return self.actions_optimizer.get_action_policy()

    def pre_action_call_hook(self, *args):
        pass

    def post_action_call_hook(self, *args):
        action_name = args[0]
        action_time = args[1]
        if action_name not in self.actions_calls:
            self.actions_calls[action_name] = []

        self.actions_calls[action_name].append(action_time)

    def pre_request_hook(self, *args):
        pass

    def post_request_hook(self, *args):
        request_type = args[0]
        request = args[1]
        request_time = args[2]
        if self.benchmark["jsorc"]["active"]:
            self.add_to_benchmark(request_type, request, request_time)

    def optimize(self, jsorc_interval):
        self.actions_optimizer.run(jsorc_interval)


class Kube:
    def __init__(self, in_cluster: bool, config: dict):
        if in_cluster:
            kubernetes_config.load_incluster_config()
        else:
            kubernetes_config.load_kube_config()

        self.client = ApiClient(config)
        self.core = CoreV1Api(config)
        self.api = AppsV1Api(self.client)
        self.auth = RbacAuthorizationV1Api(self.client)
        self.ping()
        self.defaults()

    def ping(self):
        res = self.client.call_api("/readyz", "GET")
        return res[1] == 200

    def create(self, api, namespace, conf):
        if api.startswith("ClusterRole"):
            self.create_apis[api](body=conf)
        else:
            self.create_apis[api](namespace=namespace, body=conf)

    def patch(self, api, name, namespace, conf):
        if api.startswith("ClusterRole"):
            self.patch_apis[api](name=name, body=conf)
        else:
            self.patch_apis[api](name=name, namespace=namespace, body=conf)

    def read(self, api: str, name: str, namespace: str = None):
        if api.startswith("ClusterRole"):
            return self.read_apis[api](name=name)
        else:
            return self.read_apis[api](name=name, namespace=namespace)

    def delete(self, api: str, name: str, namespace: str = None):
        if api.startswith("ClusterRole"):
            return self.delete_apis[api](name=name)
        else:
            return self.delete_apis[api](name=name, namespace=namespace)

    def is_running(self, name: str, namespace: str):
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

    def defaults(self):
        self.create_apis = {
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
        }
        self.patch_apis = {
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
        }
        self.delete_apis = {
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
        }
        self.read_apis = {
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
        }
