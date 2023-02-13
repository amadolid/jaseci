import os


class JsOrcSettings:
    ###############################################################################################################
    # ------------------------------------------------- DEFAULT ------------------------------------------------- #
    ###############################################################################################################

    DEFAULT_CONFIG = {"enabled": False, "quiet": False, "automated": False}

    DEFAULT_MANIFEST = {}

    UNSAFE_PARAPHRASE = "I know what I'm doing!"
    UNSAFE_KINDS = ["PersistentVolumeClaim"]

    ###############################################################################################################
    # -------------------------------------------------- JSORC -------------------------------------------------- #
    ###############################################################################################################

    JSORC_CONFIG = {
        "backoff_interval": 10,
        "pre_loaded_services": ["kube", "redis", "prome", "mail", "task", "elastic"],
    }

    ###############################################################################################################
    # -------------------------------------------------- KUBE --------------------------------------------------- #
    ###############################################################################################################

    KUBE_CONFIG = {
        "enabled": bool(os.getenv("KUBE_NAMESPACE")),
        "quiet": True,
        "automated": False,
        "namespace": os.getenv("KUBE_NAMESPACE", "default"),
        "in_cluster": True,
        "config": None,
    }

    ###############################################################################################################
    # -------------------------------------------------- REDIS -------------------------------------------------- #
    ###############################################################################################################

    REDIS_CONFIG = {
        "enabled": True,
        "quiet": False,
        "automated": True,
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": os.getenv("REDIS_PORT", "6379"),
        "db": os.getenv("REDIS_DB", "1"),
    }

    REDIS_MANIFEST = {
        "Service": [
            {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {"name": "jaseci-redis"},
                "spec": {
                    "selector": {"pod": "jaseci-redis"},
                    "ports": [{"protocol": "TCP", "port": 6379, "targetPort": 6379}],
                },
            }
        ],
        "Deployment": [
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {"name": "jaseci-redis"},
                "spec": {
                    "replicas": 1,
                    "selector": {"matchLabels": {"pod": "jaseci-redis"}},
                    "template": {
                        "metadata": {"labels": {"pod": "jaseci-redis"}},
                        "spec": {
                            "containers": [
                                {
                                    "name": "jaseci-redis-master",
                                    "image": "redis",
                                    "imagePullPolicy": "IfNotPresent",
                                    "command": [
                                        "redis-server",
                                        "/redis-master/redis.conf",
                                    ],
                                    "resources": {"limits": {"cpu": "0.2"}},
                                    "ports": [{"containerPort": 6379}],
                                    "volumeMounts": [
                                        {
                                            "mountPath": "/redis-master-data",
                                            "name": "data",
                                        },
                                        {
                                            "mountPath": "/redis-master",
                                            "name": "config",
                                        },
                                    ],
                                }
                            ],
                            "volumes": [
                                {"name": "data", "emptyDir": {}},
                                {
                                    "name": "config",
                                    "configMap": {
                                        "name": "jaseci-redis-config",
                                        "items": [
                                            {
                                                "key": "redis-config",
                                                "path": "redis.conf",
                                            }
                                        ],
                                    },
                                },
                            ],
                        },
                    },
                },
            }
        ],
        "ConfigMap": [
            {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {"name": "jaseci-redis-config"},
                "data": {
                    "redis-config": "maxmemory 1000mb\nmaxmemory-policy allkeys-lru\n"
                },
            }
        ],
    }

    ###############################################################################################################
    # -------------------------------------------------- TASK --------------------------------------------------- #
    ###############################################################################################################

    DEFAULT_REDIS_URL = (
        f'redis://{os.getenv("REDIS_HOST", "localhost")}'
        f':{os.getenv("REDIS_PORT", "6379")}/{os.getenv("REDIS_DB", "1")}'
    )

    TASK_CONFIG = {
        "enabled": True,
        "quiet": True,
        "automated": True,
        "broker_url": DEFAULT_REDIS_URL,
        "result_backend": DEFAULT_REDIS_URL,
        "broker_connection_retry_on_startup": True,
        "task_track_started": True,
        "worker_redirect_stdouts": False,
    }

    ###############################################################################################################
    # -------------------------------------------------- TASK --------------------------------------------------- #
    ###############################################################################################################

    MAIL_CONFIG = {
        "enabled": False,
        "quiet": True,
        "automated": False,
        "version": 2,
        "tls": True,
        "host": "",
        "port": 587,
        "sender": "",
        "user": "",
        "pass": "",
        "backend": "smtp",
        "templates": {
            "activation_subj": "Please activate your account!",
            "activation_body": "Thank you for creating an account!\n\n"
            "Activation Code: {{code}}\n"
            "Please click below to activate:\n{{link}}",
            "activation_html_body": "Thank you for creating an account!<br><br>"
            "Activation Code: {{code}}<br>"
            "Please click below to activate:<br>"
            "{{link}}",
            "resetpass_subj": "Password Reset for Jaseci Account",
            "resetpass_body": "Your Jaseci password reset token is: {{token}}",
            "resetpass_html_body": "Your Jaseci password reset" "token is: {{token}}",
        },
    }

    ###############################################################################################################
    # ----------------------------------------------- PROMETHEUS ------------------------------------------------ #
    ###############################################################################################################

    PROME_CONFIG = {
        "enabled": bool(os.getenv("PROME_HOST")),
        "quiet": True,
        "automated": True,
        "url": (
            f'http://{os.getenv("PROME_HOST", "localhost")}'
            f':{os.getenv("PROME_PORT", "9090")}'
        ),
    }

    PROME_MANIFEST = {
        "ServiceAccount": [
            {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "labels": {
                        "helm.sh/chart": "kube-state-metrics-4.13.0",
                        "app.kubernetes.io/managed-by": "Helm",
                        "app.kubernetes.io/component": "metrics",
                        "app.kubernetes.io/part-of": "kube-state-metrics",
                        "app.kubernetes.io/name": "kube-state-metrics",
                        "app.kubernetes.io/instance": "jaseci-prometheus",
                        "app.kubernetes.io/version": "2.5.0",
                    },
                    "name": "jaseci-prometheus-kube-state-metrics",
                },
                "imagePullSecrets": [],
            },
            {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "labels": {
                        "component": "alertmanager",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-alertmanager",
                    "annotations": {},
                },
            },
            {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "labels": {
                        "component": "node-exporter",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-node-exporter",
                    "annotations": {},
                },
            },
            {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "labels": {
                        "component": "pushgateway",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-pushgateway",
                    "annotations": {},
                },
            },
            {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "labels": {
                        "component": "server",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-server",
                    "annotations": {},
                },
            },
        ],
        "ConfigMap": [
            {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "labels": {
                        "component": "alertmanager",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-alertmanager",
                },
                "data": {
                    "allow-snippet-annotations": "false",
                    "alertmanager.yml": "global: {}\nreceivers:\n- name: default-receiver\nroute:\n  group_interval: 5m\n  group_wait: 10s\n  receiver: default-receiver\n  repeat_interval: 3h\n",
                },
            },
            {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "labels": {
                        "component": "server",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-server",
                },
                "data": {
                    "allow-snippet-annotations": "false",
                    "alerting_rules.yml": "{}\n",
                    "alerts": "{}\n",
                    "prometheus.yml": 'global:\n  evaluation_interval: 1m\n  scrape_interval: 1m\n  scrape_timeout: 10s\nrule_files:\n- /etc/config/recording_rules.yml\n- /etc/config/alerting_rules.yml\n- /etc/config/rules\n- /etc/config/alerts\nscrape_configs:\n- job_name: prometheus\n  static_configs:\n  - targets:\n    - localhost:9090\n- bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token\n  job_name: kubernetes-apiservers\n  kubernetes_sd_configs:\n  - role: endpoints\n  relabel_configs:\n  - action: keep\n    regex: default;kubernetes;https\n    source_labels:\n    - __meta_kubernetes_namespace\n    - __meta_kubernetes_service_name\n    - __meta_kubernetes_endpoint_port_name\n  scheme: https\n  tls_config:\n    ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt\n    insecure_skip_verify: true\n- bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token\n  job_name: kubernetes-nodes\n  kubernetes_sd_configs:\n  - role: node\n  relabel_configs:\n  - action: labelmap\n    regex: __meta_kubernetes_node_label_(.+)\n  - replacement: kubernetes.default.svc:443\n    target_label: __address__\n  - regex: (.+)\n    replacement: /api/v1/nodes/$1/proxy/metrics\n    source_labels:\n    - __meta_kubernetes_node_name\n    target_label: __metrics_path__\n  scheme: https\n  tls_config:\n    ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt\n    insecure_skip_verify: true\n- bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token\n  job_name: kubernetes-nodes-cadvisor\n  kubernetes_sd_configs:\n  - role: node\n  relabel_configs:\n  - action: labelmap\n    regex: __meta_kubernetes_node_label_(.+)\n  - replacement: kubernetes.default.svc:443\n    target_label: __address__\n  - regex: (.+)\n    replacement: /api/v1/nodes/$1/proxy/metrics/cadvisor\n    source_labels:\n    - __meta_kubernetes_node_name\n    target_label: __metrics_path__\n  scheme: https\n  tls_config:\n    ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt\n    insecure_skip_verify: true\n- honor_labels: true\n  job_name: kubernetes-service-endpoints\n  kubernetes_sd_configs:\n  - role: endpoints\n  relabel_configs:\n  - action: keep\n    regex: true\n    source_labels:\n    - __meta_kubernetes_service_annotation_prometheus_io_scrape\n  - action: drop\n    regex: true\n    source_labels:\n    - __meta_kubernetes_service_annotation_prometheus_io_scrape_slow\n  - action: replace\n    regex: (https?)\n    source_labels:\n    - __meta_kubernetes_service_annotation_prometheus_io_scheme\n    target_label: __scheme__\n  - action: replace\n    regex: (.+)\n    source_labels:\n    - __meta_kubernetes_service_annotation_prometheus_io_path\n    target_label: __metrics_path__\n  - action: replace\n    regex: (.+?)(?::\\d+)?;(\\d+)\n    replacement: $1:$2\n    source_labels:\n    - __address__\n    - __meta_kubernetes_service_annotation_prometheus_io_port\n    target_label: __address__\n  - action: labelmap\n    regex: __meta_kubernetes_service_annotation_prometheus_io_param_(.+)\n    replacement: __param_$1\n  - action: labelmap\n    regex: __meta_kubernetes_service_label_(.+)\n  - action: replace\n    source_labels:\n    - __meta_kubernetes_namespace\n    target_label: namespace\n  - action: replace\n    source_labels:\n    - __meta_kubernetes_service_name\n    target_label: service\n  - action: replace\n    source_labels:\n    - __meta_kubernetes_pod_node_name\n    target_label: node\n- honor_labels: true\n  job_name: kubernetes-service-endpoints-slow\n  kubernetes_sd_configs:\n  - role: endpoints\n  relabel_configs:\n  - action: keep\n    regex: true\n    source_labels:\n    - __meta_kubernetes_service_annotation_prometheus_io_scrape_slow\n  - action: replace\n    regex: (https?)\n    source_labels:\n    - __meta_kubernetes_service_annotation_prometheus_io_scheme\n    target_label: __scheme__\n  - action: replace\n    regex: (.+)\n    source_labels:\n    - __meta_kubernetes_service_annotation_prometheus_io_path\n    target_label: __metrics_path__\n  - action: replace\n    regex: (.+?)(?::\\d+)?;(\\d+)\n    replacement: $1:$2\n    source_labels:\n    - __address__\n    - __meta_kubernetes_service_annotation_prometheus_io_port\n    target_label: __address__\n  - action: labelmap\n    regex: __meta_kubernetes_service_annotation_prometheus_io_param_(.+)\n    replacement: __param_$1\n  - action: labelmap\n    regex: __meta_kubernetes_service_label_(.+)\n  - action: replace\n    source_labels:\n    - __meta_kubernetes_namespace\n    target_label: namespace\n  - action: replace\n    source_labels:\n    - __meta_kubernetes_service_name\n    target_label: service\n  - action: replace\n    source_labels:\n    - __meta_kubernetes_pod_node_name\n    target_label: node\n  scrape_interval: 5m\n  scrape_timeout: 30s\n- honor_labels: true\n  job_name: prometheus-pushgateway\n  kubernetes_sd_configs:\n  - role: service\n  relabel_configs:\n  - action: keep\n    regex: pushgateway\n    source_labels:\n    - __meta_kubernetes_service_annotation_prometheus_io_probe\n- honor_labels: true\n  job_name: kubernetes-services\n  kubernetes_sd_configs:\n  - role: service\n  metrics_path: /probe\n  params:\n    module:\n    - http_2xx\n  relabel_configs:\n  - action: keep\n    regex: true\n    source_labels:\n    - __meta_kubernetes_service_annotation_prometheus_io_probe\n  - source_labels:\n    - __address__\n    target_label: __param_target\n  - replacement: blackbox\n    target_label: __address__\n  - source_labels:\n    - __param_target\n    target_label: instance\n  - action: labelmap\n    regex: __meta_kubernetes_service_label_(.+)\n  - source_labels:\n    - __meta_kubernetes_namespace\n    target_label: namespace\n  - source_labels:\n    - __meta_kubernetes_service_name\n    target_label: service\n- honor_labels: true\n  job_name: kubernetes-pods\n  kubernetes_sd_configs:\n  - role: pod\n  relabel_configs:\n  - action: keep\n    regex: true\n    source_labels:\n    - __meta_kubernetes_pod_annotation_prometheus_io_scrape\n  - action: drop\n    regex: true\n    source_labels:\n    - __meta_kubernetes_pod_annotation_prometheus_io_scrape_slow\n  - action: replace\n    regex: (https?)\n    source_labels:\n    - __meta_kubernetes_pod_annotation_prometheus_io_scheme\n    target_label: __scheme__\n  - action: replace\n    regex: (.+)\n    source_labels:\n    - __meta_kubernetes_pod_annotation_prometheus_io_path\n    target_label: __metrics_path__\n  - action: replace\n    regex: (.+?)(?::\\d+)?;(\\d+)\n    replacement: $1:$2\n    source_labels:\n    - __address__\n    - __meta_kubernetes_pod_annotation_prometheus_io_port\n    target_label: __address__\n  - action: labelmap\n    regex: __meta_kubernetes_pod_annotation_prometheus_io_param_(.+)\n    replacement: __param_$1\n  - action: labelmap\n    regex: __meta_kubernetes_pod_label_(.+)\n  - action: replace\n    source_labels:\n    - __meta_kubernetes_namespace\n    target_label: namespace\n  - action: replace\n    source_labels:\n    - __meta_kubernetes_pod_name\n    target_label: pod\n  - action: drop\n    regex: Pending|Succeeded|Failed|Completed\n    source_labels:\n    - __meta_kubernetes_pod_phase\n- honor_labels: true\n  job_name: kubernetes-pods-slow\n  kubernetes_sd_configs:\n  - role: pod\n  relabel_configs:\n  - action: keep\n    regex: true\n    source_labels:\n    - __meta_kubernetes_pod_annotation_prometheus_io_scrape_slow\n  - action: replace\n    regex: (https?)\n    source_labels:\n    - __meta_kubernetes_pod_annotation_prometheus_io_scheme\n    target_label: __scheme__\n  - action: replace\n    regex: (.+)\n    source_labels:\n    - __meta_kubernetes_pod_annotation_prometheus_io_path\n    target_label: __metrics_path__\n  - action: replace\n    regex: (.+?)(?::\\d+)?;(\\d+)\n    replacement: $1:$2\n    source_labels:\n    - __address__\n    - __meta_kubernetes_pod_annotation_prometheus_io_port\n    target_label: __address__\n  - action: labelmap\n    regex: __meta_kubernetes_pod_annotation_prometheus_io_param_(.+)\n    replacement: __param_$1\n  - action: labelmap\n    regex: __meta_kubernetes_pod_label_(.+)\n  - action: replace\n    source_labels:\n    - __meta_kubernetes_namespace\n    target_label: namespace\n  - action: replace\n    source_labels:\n    - __meta_kubernetes_pod_name\n    target_label: pod\n  - action: drop\n    regex: Pending|Succeeded|Failed|Completed\n    source_labels:\n    - __meta_kubernetes_pod_phase\n  scrape_interval: 5m\n  scrape_timeout: 30s\nalerting:\n  alertmanagers:\n  - kubernetes_sd_configs:\n      - role: pod\n    tls_config:\n      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt\n    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token\n    relabel_configs:\n    - source_labels: [__meta_kubernetes_namespace]\n      regex: default\n      action: keep\n    - source_labels: [__meta_kubernetes_pod_label_app]\n      regex: prometheus\n      action: keep\n    - source_labels: [__meta_kubernetes_pod_label_component]\n      regex: alertmanager\n      action: keep\n    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_probe]\n      regex: .*\n      action: keep\n    - source_labels: [__meta_kubernetes_pod_container_port_number]\n      regex: "9093"\n      action: keep\n',
                    "recording_rules.yml": "{}\n",
                    "rules": "{}\n",
                },
            },
        ],
        "PersistentVolumeClaim": [
            {
                "apiVersion": "v1",
                "kind": "PersistentVolumeClaim",
                "metadata": {
                    "labels": {
                        "component": "alertmanager",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-alertmanager",
                },
                "spec": {
                    "accessModes": ["ReadWriteOnce"],
                    "resources": {"requests": {"storage": "2Gi"}},
                },
            },
            {
                "apiVersion": "v1",
                "kind": "PersistentVolumeClaim",
                "metadata": {
                    "labels": {
                        "component": "server",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-server",
                },
                "spec": {
                    "accessModes": ["ReadWriteOnce"],
                    "resources": {"requests": {"storage": "8Gi"}},
                },
            },
        ],
        "ClusterRole": [
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRole",
                "metadata": {
                    "labels": {
                        "helm.sh/chart": "kube-state-metrics-4.13.0",
                        "app.kubernetes.io/managed-by": "Helm",
                        "app.kubernetes.io/component": "metrics",
                        "app.kubernetes.io/part-of": "kube-state-metrics",
                        "app.kubernetes.io/name": "kube-state-metrics",
                        "app.kubernetes.io/instance": "jaseci-prometheus",
                        "app.kubernetes.io/version": "2.5.0",
                    },
                    "name": "jaseci-prometheus-kube-state-metrics",
                },
                "rules": [
                    {
                        "apiGroups": ["certificates.k8s.io"],
                        "resources": ["certificatesigningrequests"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["configmaps"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": ["batch"],
                        "resources": ["cronjobs"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": ["extensions", "apps"],
                        "resources": ["daemonsets"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": ["extensions", "apps"],
                        "resources": ["deployments"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["endpoints"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": ["autoscaling"],
                        "resources": ["horizontalpodautoscalers"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": ["extensions", "networking.k8s.io"],
                        "resources": ["ingresses"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": ["batch"],
                        "resources": ["jobs"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["limitranges"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": ["admissionregistration.k8s.io"],
                        "resources": ["mutatingwebhookconfigurations"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["namespaces"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": ["networking.k8s.io"],
                        "resources": ["networkpolicies"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["nodes"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["persistentvolumeclaims"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["persistentvolumes"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": ["policy"],
                        "resources": ["poddisruptionbudgets"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["pods"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": ["extensions", "apps"],
                        "resources": ["replicasets"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["replicationcontrollers"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["resourcequotas"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["secrets"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["services"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": ["apps"],
                        "resources": ["statefulsets"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": ["storage.k8s.io"],
                        "resources": ["storageclasses"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": ["admissionregistration.k8s.io"],
                        "resources": ["validatingwebhookconfigurations"],
                        "verbs": ["list", "watch"],
                    },
                    {
                        "apiGroups": ["storage.k8s.io"],
                        "resources": ["volumeattachments"],
                        "verbs": ["list", "watch"],
                    },
                ],
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRole",
                "metadata": {
                    "labels": {
                        "component": "alertmanager",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-alertmanager",
                },
                "rules": [],
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRole",
                "metadata": {
                    "labels": {
                        "component": "pushgateway",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-pushgateway",
                },
                "rules": [],
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRole",
                "metadata": {
                    "labels": {
                        "component": "server",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-server",
                },
                "rules": [
                    {
                        "apiGroups": [""],
                        "resources": [
                            "nodes",
                            "nodes/proxy",
                            "nodes/metrics",
                            "services",
                            "endpoints",
                            "pods",
                            "ingresses",
                            "configmaps",
                        ],
                        "verbs": ["get", "list", "watch"],
                    },
                    {
                        "apiGroups": ["extensions", "networking.k8s.io"],
                        "resources": ["ingresses/status", "ingresses"],
                        "verbs": ["get", "list", "watch"],
                    },
                    {"nonResourceURLs": ["/metrics"], "verbs": ["get"]},
                ],
            },
        ],
        "ClusterRoleBinding": [
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRoleBinding",
                "metadata": {
                    "labels": {
                        "helm.sh/chart": "kube-state-metrics-4.13.0",
                        "app.kubernetes.io/managed-by": "Helm",
                        "app.kubernetes.io/component": "metrics",
                        "app.kubernetes.io/part-of": "kube-state-metrics",
                        "app.kubernetes.io/name": "kube-state-metrics",
                        "app.kubernetes.io/instance": "jaseci-prometheus",
                        "app.kubernetes.io/version": "2.5.0",
                    },
                    "name": "jaseci-prometheus-kube-state-metrics",
                },
                "roleRef": {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": "ClusterRole",
                    "name": "jaseci-prometheus-kube-state-metrics",
                },
                "subjects": [
                    {
                        "kind": "ServiceAccount",
                        "name": "jaseci-prometheus-kube-state-metrics",
                        "namespace": "default",
                    }
                ],
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRoleBinding",
                "metadata": {
                    "labels": {
                        "component": "alertmanager",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-alertmanager",
                },
                "subjects": [
                    {
                        "kind": "ServiceAccount",
                        "name": "jaseci-prometheus-alertmanager",
                        "namespace": "default",
                    }
                ],
                "roleRef": {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": "ClusterRole",
                    "name": "jaseci-prometheus-alertmanager",
                },
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRoleBinding",
                "metadata": {
                    "labels": {
                        "component": "pushgateway",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-pushgateway",
                },
                "subjects": [
                    {
                        "kind": "ServiceAccount",
                        "name": "jaseci-prometheus-pushgateway",
                        "namespace": "default",
                    }
                ],
                "roleRef": {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": "ClusterRole",
                    "name": "jaseci-prometheus-pushgateway",
                },
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRoleBinding",
                "metadata": {
                    "labels": {
                        "component": "server",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-server",
                },
                "subjects": [
                    {
                        "kind": "ServiceAccount",
                        "name": "jaseci-prometheus-server",
                        "namespace": "default",
                    }
                ],
                "roleRef": {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": "ClusterRole",
                    "name": "jaseci-prometheus-server",
                },
            },
        ],
        "Service": [
            {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "jaseci-prometheus-kube-state-metrics",
                    "labels": {
                        "helm.sh/chart": "kube-state-metrics-4.13.0",
                        "app.kubernetes.io/managed-by": "Helm",
                        "app.kubernetes.io/component": "metrics",
                        "app.kubernetes.io/part-of": "kube-state-metrics",
                        "app.kubernetes.io/name": "kube-state-metrics",
                        "app.kubernetes.io/instance": "jaseci-prometheus",
                        "app.kubernetes.io/version": "2.5.0",
                    },
                    "annotations": {"prometheus.io/scrape": "true"},
                },
                "spec": {
                    "type": "ClusterIP",
                    "ports": [
                        {
                            "name": "http",
                            "protocol": "TCP",
                            "port": 8080,
                            "targetPort": 8080,
                        }
                    ],
                    "selector": {
                        "app.kubernetes.io/name": "kube-state-metrics",
                        "app.kubernetes.io/instance": "jaseci-prometheus",
                    },
                },
            },
            {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "labels": {
                        "component": "alertmanager",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-alertmanager",
                },
                "spec": {
                    "ports": [
                        {
                            "name": "http",
                            "port": 80,
                            "protocol": "TCP",
                            "targetPort": 9093,
                        }
                    ],
                    "selector": {
                        "component": "alertmanager",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                    },
                    "sessionAffinity": "None",
                    "type": "ClusterIP",
                },
            },
            {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "annotations": {"prometheus.io/scrape": "true"},
                    "labels": {
                        "component": "node-exporter",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-node-exporter",
                },
                "spec": {
                    "ports": [
                        {
                            "name": "metrics",
                            "port": 9100,
                            "protocol": "TCP",
                            "targetPort": 9100,
                        }
                    ],
                    "selector": {
                        "component": "node-exporter",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                    },
                    "type": "ClusterIP",
                },
            },
            {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "annotations": {"prometheus.io/probe": "pushgateway"},
                    "labels": {
                        "component": "pushgateway",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-pushgateway",
                },
                "spec": {
                    "ports": [
                        {
                            "name": "http",
                            "port": 9091,
                            "protocol": "TCP",
                            "targetPort": 9091,
                        }
                    ],
                    "selector": {
                        "component": "pushgateway",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                    },
                    "type": "ClusterIP",
                },
            },
            {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "labels": {
                        "component": "server",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-server",
                },
                "spec": {
                    "ports": [
                        {
                            "name": "http",
                            "port": 9090,
                            "protocol": "TCP",
                            "targetPort": 9090,
                        }
                    ],
                    "selector": {
                        "component": "server",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                    },
                    "sessionAffinity": "None",
                    "type": "ClusterIP",
                },
            },
        ],
        "DaemonSet": [
            {
                "apiVersion": "apps/v1",
                "kind": "DaemonSet",
                "metadata": {
                    "labels": {
                        "component": "node-exporter",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-node-exporter",
                },
                "spec": {
                    "selector": {
                        "matchLabels": {
                            "component": "node-exporter",
                            "app": "prometheus",
                            "release": "jaseci-prometheus",
                        }
                    },
                    "updateStrategy": {"type": "RollingUpdate"},
                    "template": {
                        "metadata": {
                            "labels": {
                                "component": "node-exporter",
                                "app": "prometheus",
                                "release": "jaseci-prometheus",
                                "chart": "prometheus-15.10.5",
                                "heritage": "Helm",
                            }
                        },
                        "spec": {
                            "serviceAccountName": "jaseci-prometheus-node-exporter",
                            "containers": [
                                {
                                    "name": "prometheus-node-exporter",
                                    "image": "quay.io/prometheus/node-exporter:v1.3.1",
                                    "imagePullPolicy": "IfNotPresent",
                                    "args": [
                                        "--path.procfs=/host/proc",
                                        "--path.sysfs=/host/sys",
                                        "--web.listen-address=:9100",
                                    ],
                                    "ports": [
                                        {
                                            "name": "metrics",
                                            "containerPort": 9100,
                                            "hostPort": 9100,
                                        }
                                    ],
                                    "resources": {},
                                    "securityContext": {
                                        "allowPrivilegeEscalation": False
                                    },
                                    "volumeMounts": [
                                        {
                                            "name": "proc",
                                            "mountPath": "/host/proc",
                                            "readOnly": True,
                                        },
                                        {
                                            "name": "sys",
                                            "mountPath": "/host/sys",
                                            "readOnly": True,
                                        },
                                    ],
                                }
                            ],
                            "hostNetwork": True,
                            "hostPID": True,
                            "securityContext": {
                                "fsGroup": 65534,
                                "runAsGroup": 65534,
                                "runAsNonRoot": True,
                                "runAsUser": 65534,
                            },
                            "volumes": [
                                {"name": "proc", "hostPath": {"path": "/proc"}},
                                {"name": "sys", "hostPath": {"path": "/sys"}},
                            ],
                        },
                    },
                },
            }
        ],
        "Deployment": [
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "jaseci-prometheus-kube-state-metrics",
                    "labels": {
                        "helm.sh/chart": "kube-state-metrics-4.13.0",
                        "app.kubernetes.io/managed-by": "Helm",
                        "app.kubernetes.io/component": "metrics",
                        "app.kubernetes.io/part-of": "kube-state-metrics",
                        "app.kubernetes.io/name": "kube-state-metrics",
                        "app.kubernetes.io/instance": "jaseci-prometheus",
                        "app.kubernetes.io/version": "2.5.0",
                    },
                },
                "spec": {
                    "selector": {
                        "matchLabels": {
                            "app.kubernetes.io/name": "kube-state-metrics",
                            "app.kubernetes.io/instance": "jaseci-prometheus",
                        }
                    },
                    "replicas": 1,
                    "template": {
                        "metadata": {
                            "labels": {
                                "helm.sh/chart": "kube-state-metrics-4.13.0",
                                "app.kubernetes.io/managed-by": "Helm",
                                "app.kubernetes.io/component": "metrics",
                                "app.kubernetes.io/part-of": "kube-state-metrics",
                                "app.kubernetes.io/name": "kube-state-metrics",
                                "app.kubernetes.io/instance": "jaseci-prometheus",
                                "app.kubernetes.io/version": "2.5.0",
                            }
                        },
                        "spec": {
                            "hostNetwork": False,
                            "serviceAccountName": "jaseci-prometheus-kube-state-metrics",
                            "securityContext": {
                                "fsGroup": 65534,
                                "runAsGroup": 65534,
                                "runAsUser": 65534,
                            },
                            "containers": [
                                {
                                    "name": "kube-state-metrics",
                                    "args": [
                                        "--port=8080",
                                        "--resources=certificatesigningrequests,configmaps,cronjobs,daemonsets,deployments,endpoints,horizontalpodautoscalers,ingresses,jobs,limitranges,mutatingwebhookconfigurations,namespaces,networkpolicies,nodes,persistentvolumeclaims,persistentvolumes,poddisruptionbudgets,pods,replicasets,replicationcontrollers,resourcequotas,secrets,services,statefulsets,storageclasses,validatingwebhookconfigurations,volumeattachments",
                                        "--telemetry-port=8081",
                                    ],
                                    "imagePullPolicy": "IfNotPresent",
                                    "image": "registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.5.0",
                                    "ports": [{"containerPort": 8080, "name": "http"}],
                                    "livenessProbe": {
                                        "httpGet": {"path": "/healthz", "port": 8080},
                                        "initialDelaySeconds": 5,
                                        "timeoutSeconds": 5,
                                    },
                                    "readinessProbe": {
                                        "httpGet": {"path": "/", "port": 8080},
                                        "initialDelaySeconds": 5,
                                        "timeoutSeconds": 5,
                                    },
                                }
                            ],
                        },
                    },
                },
            },
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "labels": {
                        "component": "alertmanager",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-alertmanager",
                },
                "spec": {
                    "selector": {
                        "matchLabels": {
                            "component": "alertmanager",
                            "app": "prometheus",
                            "release": "jaseci-prometheus",
                        }
                    },
                    "replicas": 1,
                    "template": {
                        "metadata": {
                            "labels": {
                                "component": "alertmanager",
                                "app": "prometheus",
                                "release": "jaseci-prometheus",
                                "chart": "prometheus-15.10.5",
                                "heritage": "Helm",
                            }
                        },
                        "spec": {
                            "serviceAccountName": "jaseci-prometheus-alertmanager",
                            "containers": [
                                {
                                    "name": "prometheus-alertmanager",
                                    "image": "quay.io/prometheus/alertmanager:v0.24.0",
                                    "imagePullPolicy": "IfNotPresent",
                                    "securityContext": {},
                                    "env": [
                                        {
                                            "name": "POD_IP",
                                            "valueFrom": {
                                                "fieldRef": {
                                                    "apiVersion": "v1",
                                                    "fieldPath": "status.podIP",
                                                }
                                            },
                                        }
                                    ],
                                    "args": [
                                        "--config.file=/etc/config/alertmanager.yml",
                                        "--storage.path=/data",
                                        "--cluster.listen-address=",
                                        "--web.external-url=http://localhost:9093",
                                    ],
                                    "ports": [{"containerPort": 9093}],
                                    "readinessProbe": {
                                        "httpGet": {"path": "/-/ready", "port": 9093},
                                        "initialDelaySeconds": 30,
                                        "timeoutSeconds": 30,
                                    },
                                    "resources": {},
                                    "volumeMounts": [
                                        {
                                            "name": "config-volume",
                                            "mountPath": "/etc/config",
                                        },
                                        {
                                            "name": "storage-volume",
                                            "mountPath": "/data",
                                            "subPath": "",
                                        },
                                    ],
                                },
                                {
                                    "name": "prometheus-alertmanager-configmap-reload",
                                    "image": "jimmidyson/configmap-reload:v0.5.0",
                                    "imagePullPolicy": "IfNotPresent",
                                    "securityContext": {},
                                    "args": [
                                        "--volume-dir=/etc/config",
                                        "--webhook-url=http://127.0.0.1:9093/-/reload",
                                    ],
                                    "resources": {},
                                    "volumeMounts": [
                                        {
                                            "name": "config-volume",
                                            "mountPath": "/etc/config",
                                            "readOnly": True,
                                        }
                                    ],
                                },
                            ],
                            "securityContext": {
                                "fsGroup": 65534,
                                "runAsGroup": 65534,
                                "runAsNonRoot": True,
                                "runAsUser": 65534,
                            },
                            "volumes": [
                                {
                                    "name": "config-volume",
                                    "configMap": {
                                        "name": "jaseci-prometheus-alertmanager"
                                    },
                                },
                                {
                                    "name": "storage-volume",
                                    "persistentVolumeClaim": {
                                        "claimName": "jaseci-prometheus-alertmanager"
                                    },
                                },
                            ],
                        },
                    },
                },
            },
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "labels": {
                        "component": "pushgateway",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                    },
                    "name": "jaseci-prometheus-pushgateway",
                },
                "spec": {
                    "selector": {
                        "matchLabels": {
                            "component": "pushgateway",
                            "app": "prometheus",
                            "release": "jaseci-prometheus",
                        }
                    },
                    "replicas": 1,
                    "template": {
                        "metadata": {
                            "labels": {
                                "component": "pushgateway",
                                "app": "prometheus",
                                "release": "jaseci-prometheus",
                                "chart": "prometheus-15.10.5",
                                "heritage": "Helm",
                            }
                        },
                        "spec": {
                            "serviceAccountName": "jaseci-prometheus-pushgateway",
                            "containers": [
                                {
                                    "name": "prometheus-pushgateway",
                                    "image": "prom/pushgateway:v1.4.3",
                                    "imagePullPolicy": "IfNotPresent",
                                    "securityContext": {},
                                    "args": None,
                                    "ports": [{"containerPort": 9091}],
                                    "livenessProbe": {
                                        "httpGet": {"path": "/-/healthy", "port": 9091},
                                        "initialDelaySeconds": 10,
                                        "timeoutSeconds": 10,
                                    },
                                    "readinessProbe": {
                                        "httpGet": {"path": "/-/ready", "port": 9091},
                                        "initialDelaySeconds": 10,
                                        "timeoutSeconds": 10,
                                    },
                                    "resources": {},
                                }
                            ],
                            "securityContext": {
                                "runAsNonRoot": True,
                                "runAsUser": 65534,
                            },
                        },
                    },
                },
            },
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "labels": {
                        "component": "server",
                        "app": "prometheus",
                        "release": "jaseci-prometheus",
                        "chart": "prometheus-15.10.5",
                        "heritage": "Helm",
                        "pod": "jaseci-prometheus-server",
                    },
                    "name": "jaseci-prometheus-server",
                },
                "spec": {
                    "selector": {
                        "matchLabels": {
                            "component": "server",
                            "app": "prometheus",
                            "release": "jaseci-prometheus",
                        }
                    },
                    "replicas": 1,
                    "template": {
                        "metadata": {
                            "labels": {
                                "component": "server",
                                "app": "prometheus",
                                "release": "jaseci-prometheus",
                                "chart": "prometheus-15.10.5",
                                "heritage": "Helm",
                                "pod": "jaseci-prometheus-server",
                            }
                        },
                        "spec": {
                            "enableServiceLinks": True,
                            "serviceAccountName": "jaseci-prometheus-server",
                            "containers": [
                                {
                                    "name": "prometheus-server-configmap-reload",
                                    "image": "jimmidyson/configmap-reload:v0.5.0",
                                    "imagePullPolicy": "IfNotPresent",
                                    "securityContext": {},
                                    "args": [
                                        "--volume-dir=/etc/config",
                                        "--webhook-url=http://127.0.0.1:9090/-/reload",
                                    ],
                                    "resources": {},
                                    "volumeMounts": [
                                        {
                                            "name": "config-volume",
                                            "mountPath": "/etc/config",
                                            "readOnly": True,
                                        }
                                    ],
                                },
                                {
                                    "name": "prometheus-server",
                                    "image": "quay.io/prometheus/prometheus:v2.36.2",
                                    "imagePullPolicy": "IfNotPresent",
                                    "securityContext": {},
                                    "args": [
                                        "--storage.tsdb.retention.time=15d",
                                        "--config.file=/etc/config/prometheus.yml",
                                        "--storage.tsdb.path=/data",
                                        "--web.console.libraries=/etc/prometheus/console_libraries",
                                        "--web.console.templates=/etc/prometheus/consoles",
                                        "--web.enable-lifecycle",
                                    ],
                                    "ports": [{"containerPort": 9090}],
                                    "readinessProbe": {
                                        "httpGet": {
                                            "path": "/-/ready",
                                            "port": 9090,
                                            "scheme": "HTTP",
                                        },
                                        "initialDelaySeconds": 30,
                                        "periodSeconds": 5,
                                        "timeoutSeconds": 4,
                                        "failureThreshold": 3,
                                        "successThreshold": 1,
                                    },
                                    "livenessProbe": {
                                        "httpGet": {
                                            "path": "/-/healthy",
                                            "port": 9090,
                                            "scheme": "HTTP",
                                        },
                                        "initialDelaySeconds": 30,
                                        "periodSeconds": 15,
                                        "timeoutSeconds": 10,
                                        "failureThreshold": 3,
                                        "successThreshold": 1,
                                    },
                                    "resources": {},
                                    "volumeMounts": [
                                        {
                                            "name": "config-volume",
                                            "mountPath": "/etc/config",
                                        },
                                        {
                                            "name": "storage-volume",
                                            "mountPath": "/data",
                                            "subPath": "",
                                        },
                                    ],
                                },
                            ],
                            "hostNetwork": False,
                            "dnsPolicy": "ClusterFirst",
                            "securityContext": {
                                "fsGroup": 65534,
                                "runAsGroup": 65534,
                                "runAsNonRoot": True,
                                "runAsUser": 65534,
                            },
                            "terminationGracePeriodSeconds": 300,
                            "volumes": [
                                {
                                    "name": "config-volume",
                                    "configMap": {"name": "jaseci-prometheus-server"},
                                },
                                {
                                    "name": "storage-volume",
                                    "persistentVolumeClaim": {
                                        "claimName": "jaseci-prometheus-server"
                                    },
                                },
                            ],
                        },
                    },
                },
            },
        ],
    }

    ###############################################################################################################
    # ------------------------------------------------ ELASTIC -------------------------------------------------- #
    ###############################################################################################################

    ELASTIC_CONFIG = {
        "enabled": False,
        "quiet": True,
        "url": "",
        "auth": "",
        "common_index": "",
        "activity_index": "",
    }

    ELASTIC_MANIFEST = {
        "CustomResourceDefinition": [
            {
                "apiVersion": "apiextensions.k8s.io/v1",
                "kind": "CustomResourceDefinition",
                "metadata": {
                    "annotations": {"controller-gen.kubebuilder.io/version": "v0.10.0"},
                    "creationTimestamp": None,
                    "labels": {
                        "app.kubernetes.io/instance": "elastic-operator",
                        "app.kubernetes.io/name": "eck-operator-crds",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                    "name": "agents.agent.k8s.elastic.co",
                },
                "spec": {
                    "group": "agent.k8s.elastic.co",
                    "names": {
                        "categories": ["elastic"],
                        "kind": "Agent",
                        "listKind": "AgentList",
                        "plural": "agents",
                        "shortNames": ["agent"],
                        "singular": "agent",
                    },
                    "scope": "Namespaced",
                    "versions": [
                        {
                            "additionalPrinterColumns": [
                                {
                                    "jsonPath": ".status.health",
                                    "name": "health",
                                    "type": "string",
                                },
                                {
                                    "description": "Available nodes",
                                    "jsonPath": ".status.availableNodes",
                                    "name": "available",
                                    "type": "integer",
                                },
                                {
                                    "description": "Expected nodes",
                                    "jsonPath": ".status.expectedNodes",
                                    "name": "expected",
                                    "type": "integer",
                                },
                                {
                                    "description": "Agent version",
                                    "jsonPath": ".status.version",
                                    "name": "version",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".metadata.creationTimestamp",
                                    "name": "age",
                                    "type": "date",
                                },
                            ],
                            "name": "v1alpha1",
                            "schema": {
                                "openAPIV3Schema": {
                                    "description": "Agent is the Schema for the Agents API.",
                                    "properties": {
                                        "apiVersion": {
                                            "description": "APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources",
                                            "type": "string",
                                        },
                                        "kind": {
                                            "description": "Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds",
                                            "type": "string",
                                        },
                                        "metadata": {"type": "object"},
                                        "spec": {
                                            "description": "AgentSpec defines the desired state of the Agent",
                                            "properties": {
                                                "config": {
                                                    "description": "Config holds the Agent configuration. At most one of [`Config`, `ConfigRef`] can be specified.",
                                                    "type": "object",
                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                },
                                                "configRef": {
                                                    "description": 'ConfigRef contains a reference to an existing Kubernetes Secret holding the Agent configuration. Agent settings must be specified as yaml, under a single "agent.yml" entry. At most one of [`Config`, `ConfigRef`] can be specified.',
                                                    "properties": {
                                                        "secretName": {
                                                            "description": "SecretName is the name of the secret.",
                                                            "type": "string",
                                                        }
                                                    },
                                                    "type": "object",
                                                },
                                                "daemonSet": {
                                                    "description": "DaemonSet specifies the Agent should be deployed as a DaemonSet, and allows providing its spec. Cannot be used along with `deployment`.",
                                                    "properties": {
                                                        "podTemplate": {
                                                            "description": "PodTemplateSpec describes the data a pod should have when created from a template",
                                                            "type": "object",
                                                            "x-kubernetes-preserve-unknown-fields": True,
                                                        },
                                                        "updateStrategy": {
                                                            "description": "DaemonSetUpdateStrategy is a struct used to control the update strategy for a DaemonSet.",
                                                            "properties": {
                                                                "rollingUpdate": {
                                                                    "description": 'Rolling update config params. Present only if type = "RollingUpdate". --- TODO: Update this to follow our convention for oneOf, whatever we decide it to be. Same as Deployment `strategy.rollingUpdate`. See https://github.com/kubernetes/kubernetes/issues/35345',
                                                                    "properties": {
                                                                        "maxSurge": {
                                                                            "anyOf": [
                                                                                {
                                                                                    "type": "integer"
                                                                                },
                                                                                {
                                                                                    "type": "string"
                                                                                },
                                                                            ],
                                                                            "description": "The maximum number of nodes with an existing available DaemonSet pod that can have an updated DaemonSet pod during during an update. Value can be an absolute number (ex: 5) or a percentage of desired pods (ex: 10%). This can not be 0 if MaxUnavailable is 0. Absolute number is calculated from percentage by rounding up to a minimum of 1. Default value is 0. Example: when this is set to 30%, at most 30% of the total number of nodes that should be running the daemon pod (i.e. status.desiredNumberScheduled) can have their a new pod created before the old pod is marked as deleted. The update starts by launching new pods on 30% of nodes. Once an updated pod is available (Ready for at least minReadySeconds) the old DaemonSet pod on that node is marked deleted. If the old pod becomes unavailable for any reason (Ready transitions to false, is evicted, or is drained) an updated pod is immediatedly created on that node without considering surge limits. Allowing surge implies the possibility that the resources consumed by the daemonset on any given node can double if the readiness check fails, and so resource intensive daemonsets should take into account that they may cause evictions during disruption.",
                                                                            "x-kubernetes-int-or-string": True,
                                                                        },
                                                                        "maxUnavailable": {
                                                                            "anyOf": [
                                                                                {
                                                                                    "type": "integer"
                                                                                },
                                                                                {
                                                                                    "type": "string"
                                                                                },
                                                                            ],
                                                                            "description": "The maximum number of DaemonSet pods that can be unavailable during the update. Value can be an absolute number (ex: 5) or a percentage of total number of DaemonSet pods at the start of the update (ex: 10%). Absolute number is calculated from percentage by rounding up. This cannot be 0 if MaxSurge is 0 Default value is 1. Example: when this is set to 30%, at most 30% of the total number of nodes that should be running the daemon pod (i.e. status.desiredNumberScheduled) can have their pods stopped for an update at any given time. The update starts by stopping at most 30% of those DaemonSet pods and then brings up new DaemonSet pods in their place. Once the new pods are available, it then proceeds onto other DaemonSet pods, thus ensuring that at least 70% of original number of DaemonSet pods are available at all times during the update.",
                                                                            "x-kubernetes-int-or-string": True,
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "type": {
                                                                    "description": 'Type of daemon set update. Can be "RollingUpdate" or "OnDelete". Default is RollingUpdate.',
                                                                    "type": "string",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "deployment": {
                                                    "description": "Deployment specifies the Agent should be deployed as a Deployment, and allows providing its spec. Cannot be used along with `daemonSet`.",
                                                    "properties": {
                                                        "podTemplate": {
                                                            "description": "PodTemplateSpec describes the data a pod should have when created from a template",
                                                            "type": "object",
                                                            "x-kubernetes-preserve-unknown-fields": True,
                                                        },
                                                        "replicas": {
                                                            "format": "int32",
                                                            "type": "integer",
                                                        },
                                                        "strategy": {
                                                            "description": "DeploymentStrategy describes how to replace existing pods with new ones.",
                                                            "properties": {
                                                                "rollingUpdate": {
                                                                    "description": "Rolling update config params. Present only if DeploymentStrategyType = RollingUpdate. --- TODO: Update this to follow our convention for oneOf, whatever we decide it to be.",
                                                                    "properties": {
                                                                        "maxSurge": {
                                                                            "anyOf": [
                                                                                {
                                                                                    "type": "integer"
                                                                                },
                                                                                {
                                                                                    "type": "string"
                                                                                },
                                                                            ],
                                                                            "description": "The maximum number of pods that can be scheduled above the desired number of pods. Value can be an absolute number (ex: 5) or a percentage of desired pods (ex: 10%). This can not be 0 if MaxUnavailable is 0. Absolute number is calculated from percentage by rounding up. Defaults to 25%. Example: when this is set to 30%, the new ReplicaSet can be scaled up immediately when the rolling update starts, such that the total number of old and new pods do not exceed 130% of desired pods. Once old pods have been killed, new ReplicaSet can be scaled up further, ensuring that total number of pods running at any time during the update is at most 130% of desired pods.",
                                                                            "x-kubernetes-int-or-string": True,
                                                                        },
                                                                        "maxUnavailable": {
                                                                            "anyOf": [
                                                                                {
                                                                                    "type": "integer"
                                                                                },
                                                                                {
                                                                                    "type": "string"
                                                                                },
                                                                            ],
                                                                            "description": "The maximum number of pods that can be unavailable during the update. Value can be an absolute number (ex: 5) or a percentage of desired pods (ex: 10%). Absolute number is calculated from percentage by rounding down. This can not be 0 if MaxSurge is 0. Defaults to 25%. Example: when this is set to 30%, the old ReplicaSet can be scaled down to 70% of desired pods immediately when the rolling update starts. Once new pods are ready, old ReplicaSet can be scaled down further, followed by scaling up the new ReplicaSet, ensuring that the total number of pods available at all times during the update is at least 70% of desired pods.",
                                                                            "x-kubernetes-int-or-string": True,
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "type": {
                                                                    "description": 'Type of deployment. Can be "Recreate" or "RollingUpdate". Default is RollingUpdate.',
                                                                    "type": "string",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "elasticsearchRefs": {
                                                    "description": "ElasticsearchRefs is a reference to a list of Elasticsearch clusters running in the same Kubernetes cluster. Due to existing limitations, only a single ES cluster is currently supported.",
                                                    "items": {
                                                        "properties": {
                                                            "name": {
                                                                "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                                "type": "string",
                                                            },
                                                            "namespace": {
                                                                "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                                "type": "string",
                                                            },
                                                            "outputName": {
                                                                "type": "string"
                                                            },
                                                            "secretName": {
                                                                "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                                "type": "string",
                                                            },
                                                            "serviceName": {
                                                                "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                                "type": "string",
                                                            },
                                                        },
                                                        "type": "object",
                                                    },
                                                    "type": "array",
                                                },
                                                "fleetServerEnabled": {
                                                    "description": "FleetServerEnabled determines whether this Agent will launch Fleet Server. Don't set unless `mode` is set to `fleet`.",
                                                    "type": "boolean",
                                                },
                                                "fleetServerRef": {
                                                    "description": "FleetServerRef is a reference to Fleet Server that this Agent should connect to to obtain it's configuration. Don't set unless `mode` is set to `fleet`.",
                                                    "properties": {
                                                        "name": {
                                                            "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                            "type": "string",
                                                        },
                                                        "namespace": {
                                                            "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                            "type": "string",
                                                        },
                                                        "secretName": {
                                                            "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                            "type": "string",
                                                        },
                                                        "serviceName": {
                                                            "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                            "type": "string",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "http": {
                                                    "description": "HTTP holds the HTTP layer configuration for the Agent in Fleet mode with Fleet Server enabled.",
                                                    "properties": {
                                                        "service": {
                                                            "description": "Service defines the template for the associated Kubernetes Service object.",
                                                            "properties": {
                                                                "metadata": {
                                                                    "description": "ObjectMeta is the metadata of the service. The name and namespace provided here are managed by ECK and will be ignored.",
                                                                    "properties": {
                                                                        "annotations": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "finalizers": {
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "labels": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "name": {
                                                                            "type": "string"
                                                                        },
                                                                        "namespace": {
                                                                            "type": "string"
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "spec": {
                                                                    "description": "Spec is the specification of the service.",
                                                                    "properties": {
                                                                        "allocateLoadBalancerNodePorts": {
                                                                            "description": 'allocateLoadBalancerNodePorts defines if NodePorts will be automatically allocated for services with type LoadBalancer.  Default is "true". It may be set to "false" if the cluster load-balancer does not rely on NodePorts.  If the caller requests specific NodePorts (by specifying a value), those requests will be respected, regardless of this field. This field may only be set for services with type LoadBalancer and will be cleared if the type is changed to any other type.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "clusterIP": {
                                                                            "description": 'clusterIP is the IP address of the service and is usually assigned randomly. If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be blank) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address. Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "clusterIPs": {
                                                                            "description": 'ClusterIPs is a list of IP addresses assigned to this service, and are usually assigned randomly.  If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be empty) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address.  Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName.  If this field is not specified, it will be initialized from the clusterIP field.  If this field is specified, clients must ensure that clusterIPs[0] and clusterIP have the same value. \n This field may hold a maximum of two entries (dual-stack IPs, in either order). These IPs must correspond to the values of the ipFamilies field. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "externalIPs": {
                                                                            "description": "externalIPs is a list of IP addresses for which nodes in the cluster will also accept traffic for this service.  These IPs are not managed by Kubernetes.  The user is responsible for ensuring that traffic arrives at a node with this IP.  A common example is external load-balancers that are not part of the Kubernetes system.",
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "externalName": {
                                                                            "description": 'externalName is the external reference that discovery mechanisms will return as an alias for this service (e.g. a DNS CNAME record). No proxying will be involved.  Must be a lowercase RFC-1123 hostname (https://tools.ietf.org/html/rfc1123) and requires `type` to be "ExternalName".',
                                                                            "type": "string",
                                                                        },
                                                                        "externalTrafficPolicy": {
                                                                            "description": 'externalTrafficPolicy describes how nodes distribute service traffic they receive on one of the Service\'s "externally-facing" addresses (NodePorts, ExternalIPs, and LoadBalancer IPs). If set to "Local", the proxy will configure the service in a way that assumes that external load balancers will take care of balancing the service traffic between nodes, and so each node will deliver traffic only to the node-local endpoints of the service, without masquerading the client source IP. (Traffic mistakenly sent to a node with no endpoints will be dropped.) The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features). Note that traffic sent to an External IP or LoadBalancer IP from within the cluster will always get "Cluster" semantics, but clients sending to a NodePort from within the cluster may need to take traffic policy into account when picking a node.',
                                                                            "type": "string",
                                                                        },
                                                                        "healthCheckNodePort": {
                                                                            "description": "healthCheckNodePort specifies the healthcheck nodePort for the service. This only applies when type is set to LoadBalancer and externalTrafficPolicy is set to Local. If a value is specified, is in-range, and is not in use, it will be used.  If not specified, a value will be automatically allocated.  External systems (e.g. load-balancers) can use this port to determine if a given node holds endpoints for this service or not.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type). This field cannot be updated once set.",
                                                                            "format": "int32",
                                                                            "type": "integer",
                                                                        },
                                                                        "internalTrafficPolicy": {
                                                                            "description": 'InternalTrafficPolicy describes how nodes distribute service traffic they receive on the ClusterIP. If set to "Local", the proxy will assume that pods only want to talk to endpoints of the service on the same node as the pod, dropping the traffic if there are no local endpoints. The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features).',
                                                                            "type": "string",
                                                                        },
                                                                        "ipFamilies": {
                                                                            "description": 'IPFamilies is a list of IP families (e.g. IPv4, IPv6) assigned to this service. This field is usually assigned automatically based on cluster configuration and the ipFamilyPolicy field. If this field is specified manually, the requested family is available in the cluster, and ipFamilyPolicy allows it, it will be used; otherwise creation of the service will fail. This field is conditionally mutable: it allows for adding or removing a secondary IP family, but it does not allow changing the primary IP family of the Service. Valid values are "IPv4" and "IPv6".  This field only applies to Services of types ClusterIP, NodePort, and LoadBalancer, and does apply to "headless" services. This field will be wiped when updating a Service to type ExternalName. \n This field may hold a maximum of two entries (dual-stack families, in either order).  These families must correspond to the values of the clusterIPs field, if specified. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field.',
                                                                            "items": {
                                                                                "description": "IPFamily represents the IP Family (IPv4 or IPv6). This type is used to express the family of an IP expressed by a type (e.g. service.spec.ipFamilies).",
                                                                                "type": "string",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "ipFamilyPolicy": {
                                                                            "description": 'IPFamilyPolicy represents the dual-stack-ness requested or required by this Service. If there is no value provided, then this field will be set to SingleStack. Services can be "SingleStack" (a single IP family), "PreferDualStack" (two IP families on dual-stack configured clusters or a single IP family on single-stack clusters), or "RequireDualStack" (two IP families on dual-stack configured clusters, otherwise fail). The ipFamilies and clusterIPs fields depend on the value of this field. This field will be wiped when updating a service to type ExternalName.',
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerClass": {
                                                                            "description": "loadBalancerClass is the class of the load balancer implementation this Service belongs to. If specified, the value of this field must be a label-style identifier, with an optional prefix, e.g. \"internal-vip\" or \"example.com/internal-vip\". Unprefixed names are reserved for end-users. This field can only be set when the Service type is 'LoadBalancer'. If not set, the default load balancer implementation is used, today this is typically done through the cloud provider integration, but should apply for any default implementation. If set, it is assumed that a load balancer implementation is watching for Services with a matching class. Any default load balancer implementation (e.g. cloud providers) should ignore Services that set this field. This field can only be set when creating or updating a Service to type 'LoadBalancer'. Once set, it can not be changed. This field will be wiped when a service is updated to a non 'LoadBalancer' type.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerIP": {
                                                                            "description": "Only applies to Service Type: LoadBalancer. This feature depends on whether the underlying cloud-provider supports specifying the loadBalancerIP when a load balancer is created. This field will be ignored if the cloud-provider does not support the feature. Deprecated: This field was under-specified and its meaning varies across implementations, and it cannot support dual-stack. As of Kubernetes v1.24, users are encouraged to use implementation-specific annotations when available. This field may be removed in a future API version.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerSourceRanges": {
                                                                            "description": 'If specified and supported by the platform, this will restrict traffic through the cloud-provider load-balancer will be restricted to the specified client IPs. This field will be ignored if the cloud-provider does not support the feature." More info: https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "ports": {
                                                                            "description": "The list of ports that are exposed by this service. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies",
                                                                            "items": {
                                                                                "description": "ServicePort contains information on service's port.",
                                                                                "properties": {
                                                                                    "appProtocol": {
                                                                                        "description": "The application protocol for this port. This field follows standard Kubernetes label syntax. Un-prefixed names are reserved for IANA standard service names (as per RFC-6335 and https://www.iana.org/assignments/service-names). Non-standard protocols should use prefixed names such as mycompany.com/my-custom-protocol.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "name": {
                                                                                        "description": "The name of this port within the service. This must be a DNS_LABEL. All ports within a ServiceSpec must have unique names. When considering the endpoints for a Service, this must match the 'name' field in the EndpointPort. Optional if only one ServicePort is defined on this service.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "nodePort": {
                                                                                        "description": "The port on each node on which this service is exposed when type is NodePort or LoadBalancer.  Usually assigned by the system. If a value is specified, in-range, and not in use it will be used, otherwise the operation will fail.  If not specified, a port will be allocated if this Service requires one.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type from NodePort to ClusterIP). More info: https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "port": {
                                                                                        "description": "The port that will be exposed by this service.",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "protocol": {
                                                                                        "default": "TCP",
                                                                                        "description": 'The IP protocol for this port. Supports "TCP", "UDP", and "SCTP". Default is TCP.',
                                                                                        "type": "string",
                                                                                    },
                                                                                    "targetPort": {
                                                                                        "anyOf": [
                                                                                            {
                                                                                                "type": "integer"
                                                                                            },
                                                                                            {
                                                                                                "type": "string"
                                                                                            },
                                                                                        ],
                                                                                        "description": "Number or name of the port to access on the pods targeted by the service. Number must be in the range 1 to 65535. Name must be an IANA_SVC_NAME. If this is a string, it will be looked up as a named port in the target Pod's container ports. If this is not specified, the value of the 'port' field is used (an identity map). This field is ignored for services with clusterIP=None, and should be omitted or set equal to the 'port' field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#defining-a-service",
                                                                                        "x-kubernetes-int-or-string": True,
                                                                                    },
                                                                                },
                                                                                "required": [
                                                                                    "port"
                                                                                ],
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-map-keys": [
                                                                                "port",
                                                                                "protocol",
                                                                            ],
                                                                            "x-kubernetes-list-type": "map",
                                                                        },
                                                                        "publishNotReadyAddresses": {
                                                                            "description": 'publishNotReadyAddresses indicates that any agent which deals with endpoints for this Service should disregard any indications of ready/not-ready. The primary use case for setting this field is for a StatefulSet\'s Headless Service to propagate SRV DNS records for its Pods for the purpose of peer discovery. The Kubernetes controllers that generate Endpoints and EndpointSlice resources for Services interpret this to mean that all endpoints are considered "ready" even if the Pods themselves are not. Agents which consume only Kubernetes generated endpoints through the Endpoints or EndpointSlice resources can safely assume this behavior.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "selector": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "description": "Route service traffic to pods with label keys and values matching this selector. If empty or not present, the service is assumed to have an external process managing its endpoints, which Kubernetes will not modify. Only applies to types ClusterIP, NodePort, and LoadBalancer. Ignored if type is ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/",
                                                                            "type": "object",
                                                                            "x-kubernetes-map-type": "atomic",
                                                                        },
                                                                        "sessionAffinity": {
                                                                            "description": 'Supports "ClientIP" and "None". Used to maintain session affinity. Enable client IP based session affinity. Must be ClientIP or None. Defaults to None. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "sessionAffinityConfig": {
                                                                            "description": "sessionAffinityConfig contains the configurations of session affinity.",
                                                                            "properties": {
                                                                                "clientIP": {
                                                                                    "description": "clientIP contains the configurations of Client IP based session affinity.",
                                                                                    "properties": {
                                                                                        "timeoutSeconds": {
                                                                                            "description": 'timeoutSeconds specifies the seconds of ClientIP type session sticky time. The value must be >0 && <=86400(for 1 day) if ServiceAffinity == "ClientIP". Default value is 10800(for 3 hours).',
                                                                                            "format": "int32",
                                                                                            "type": "integer",
                                                                                        }
                                                                                    },
                                                                                    "type": "object",
                                                                                }
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "type": {
                                                                            "description": 'type determines how the Service is exposed. Defaults to ClusterIP. Valid options are ExternalName, ClusterIP, NodePort, and LoadBalancer. "ClusterIP" allocates a cluster-internal IP address for load-balancing to endpoints. Endpoints are determined by the selector or if that is not specified, by manual construction of an Endpoints object or EndpointSlice objects. If clusterIP is "None", no virtual IP is allocated and the endpoints are published as a set of endpoints rather than a virtual IP. "NodePort" builds on ClusterIP and allocates a port on every node which routes to the same endpoints as the clusterIP. "LoadBalancer" builds on NodePort and creates an external load-balancer (if supported in the current cloud) which routes to the same endpoints as the clusterIP. "ExternalName" aliases this service to the specified externalName. Several other fields do not apply to ExternalName services. More info: https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                        "tls": {
                                                            "description": "TLS defines options for configuring TLS for HTTP.",
                                                            "properties": {
                                                                "certificate": {
                                                                    "description": "Certificate is a reference to a Kubernetes secret that contains the certificate and private key for enabling TLS. The referenced secret should contain the following: \n - `ca.crt`: The certificate authority (optional). - `tls.crt`: The certificate (or a chain). - `tls.key`: The private key to the first certificate in the certificate chain.",
                                                                    "properties": {
                                                                        "secretName": {
                                                                            "description": "SecretName is the name of the secret.",
                                                                            "type": "string",
                                                                        }
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "selfSignedCertificate": {
                                                                    "description": "SelfSignedCertificate allows configuring the self-signed certificate generated by the operator.",
                                                                    "properties": {
                                                                        "disabled": {
                                                                            "description": "Disabled indicates that the provisioning of the self-signed certifcate should be disabled.",
                                                                            "type": "boolean",
                                                                        },
                                                                        "subjectAltNames": {
                                                                            "description": "SubjectAlternativeNames is a list of SANs to include in the generated HTTP TLS certificate.",
                                                                            "items": {
                                                                                "description": "SubjectAlternativeName represents a SAN entry in a x509 certificate.",
                                                                                "properties": {
                                                                                    "dns": {
                                                                                        "description": "DNS is the DNS name of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "ip": {
                                                                                        "description": "IP is the IP address of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                },
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "image": {
                                                    "description": "Image is the Agent Docker image to deploy. Version has to match the Agent in the image.",
                                                    "type": "string",
                                                },
                                                "kibanaRef": {
                                                    "description": "KibanaRef is a reference to Kibana where Fleet should be set up and this Agent should be enrolled. Don't set unless `mode` is set to `fleet`.",
                                                    "properties": {
                                                        "name": {
                                                            "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                            "type": "string",
                                                        },
                                                        "namespace": {
                                                            "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                            "type": "string",
                                                        },
                                                        "secretName": {
                                                            "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                            "type": "string",
                                                        },
                                                        "serviceName": {
                                                            "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                            "type": "string",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "mode": {
                                                    "description": "Mode specifies the source of configuration for the Agent. The configuration can be specified locally through `config` or `configRef` (`standalone` mode), or come from Fleet during runtime (`fleet` mode). Defaults to `standalone` mode.",
                                                    "enum": ["standalone", "fleet"],
                                                    "type": "string",
                                                },
                                                "policyID": {
                                                    "description": "PolicyID optionally determines into which Agent Policy this Agent will be enrolled. If left empty the default policy will be used.",
                                                    "type": "string",
                                                },
                                                "revisionHistoryLimit": {
                                                    "description": "RevisionHistoryLimit is the number of revisions to retain to allow rollback in the underlying DaemonSet or Deployment.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "secureSettings": {
                                                    "description": "SecureSettings is a list of references to Kubernetes Secrets containing sensitive configuration options for the Agent. Secrets data can be then referenced in the Agent config using the Secret's keys or as specified in `Entries` field of each SecureSetting.",
                                                    "items": {
                                                        "description": "SecretSource defines a data source based on a Kubernetes Secret.",
                                                        "properties": {
                                                            "entries": {
                                                                "description": "Entries define how to project each key-value pair in the secret to filesystem paths. If not defined, all keys will be projected to similarly named paths in the filesystem. If defined, only the specified keys will be projected to the corresponding paths.",
                                                                "items": {
                                                                    "description": "KeyToPath defines how to map a key in a Secret object to a filesystem path.",
                                                                    "properties": {
                                                                        "key": {
                                                                            "description": "Key is the key contained in the secret.",
                                                                            "type": "string",
                                                                        },
                                                                        "path": {
                                                                            "description": 'Path is the relative file path to map the key to. Path must not be an absolute file path and must not contain any ".." components.',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "required": ["key"],
                                                                    "type": "object",
                                                                },
                                                                "type": "array",
                                                            },
                                                            "secretName": {
                                                                "description": "SecretName is the name of the secret.",
                                                                "type": "string",
                                                            },
                                                        },
                                                        "required": ["secretName"],
                                                        "type": "object",
                                                    },
                                                    "type": "array",
                                                },
                                                "serviceAccountName": {
                                                    "description": "ServiceAccountName is used to check access from the current resource to an Elasticsearch resource in a different namespace. Can only be used if ECK is enforcing RBAC on references.",
                                                    "type": "string",
                                                },
                                                "version": {
                                                    "description": "Version of the Agent.",
                                                    "type": "string",
                                                },
                                            },
                                            "required": ["version"],
                                            "type": "object",
                                        },
                                        "status": {
                                            "description": "AgentStatus defines the observed state of the Agent",
                                            "properties": {
                                                "availableNodes": {
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "elasticsearchAssociationsStatus": {
                                                    "additionalProperties": {
                                                        "description": "AssociationStatus is the status of an association resource.",
                                                        "type": "string",
                                                    },
                                                    "description": "AssociationStatusMap is the map of association's namespaced name string to its AssociationStatus. For resources that have a single Association of a given type (for ex. single ES reference), this map contains a single entry.",
                                                    "type": "object",
                                                },
                                                "expectedNodes": {
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "fleetServerAssociationStatus": {
                                                    "description": "AssociationStatus is the status of an association resource.",
                                                    "type": "string",
                                                },
                                                "health": {"type": "string"},
                                                "kibanaAssociationStatus": {
                                                    "description": "AssociationStatus is the status of an association resource.",
                                                    "type": "string",
                                                },
                                                "observedGeneration": {
                                                    "description": "ObservedGeneration is the most recent generation observed for this Elastic Agent. It corresponds to the metadata generation, which is updated on mutation by the API Server. If the generation observed in status diverges from the generation in metadata, the Elastic Agent controller has not yet processed the changes contained in the Elastic Agent specification.",
                                                    "format": "int64",
                                                    "type": "integer",
                                                },
                                                "version": {
                                                    "description": "Version of the stack resource currently running. During version upgrades, multiple versions may run in parallel: this value specifies the lowest version currently running.",
                                                    "type": "string",
                                                },
                                            },
                                            "type": "object",
                                        },
                                    },
                                    "type": "object",
                                }
                            },
                            "served": True,
                            "storage": True,
                            "subresources": {"status": {}},
                        }
                    ],
                },
            },
            {
                "apiVersion": "apiextensions.k8s.io/v1",
                "kind": "CustomResourceDefinition",
                "metadata": {
                    "annotations": {"controller-gen.kubebuilder.io/version": "v0.10.0"},
                    "creationTimestamp": None,
                    "labels": {
                        "app.kubernetes.io/instance": "elastic-operator",
                        "app.kubernetes.io/name": "eck-operator-crds",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                    "name": "apmservers.apm.k8s.elastic.co",
                },
                "spec": {
                    "group": "apm.k8s.elastic.co",
                    "names": {
                        "categories": ["elastic"],
                        "kind": "ApmServer",
                        "listKind": "ApmServerList",
                        "plural": "apmservers",
                        "shortNames": ["apm"],
                        "singular": "apmserver",
                    },
                    "scope": "Namespaced",
                    "versions": [
                        {
                            "additionalPrinterColumns": [
                                {
                                    "jsonPath": ".status.health",
                                    "name": "health",
                                    "type": "string",
                                },
                                {
                                    "description": "Available nodes",
                                    "jsonPath": ".status.availableNodes",
                                    "name": "nodes",
                                    "type": "integer",
                                },
                                {
                                    "description": "APM version",
                                    "jsonPath": ".status.version",
                                    "name": "version",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".metadata.creationTimestamp",
                                    "name": "age",
                                    "type": "date",
                                },
                            ],
                            "name": "v1",
                            "schema": {
                                "openAPIV3Schema": {
                                    "description": "ApmServer represents an APM Server resource in a Kubernetes cluster.",
                                    "properties": {
                                        "apiVersion": {
                                            "description": "APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources",
                                            "type": "string",
                                        },
                                        "kind": {
                                            "description": "Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds",
                                            "type": "string",
                                        },
                                        "metadata": {"type": "object"},
                                        "spec": {
                                            "description": "ApmServerSpec holds the specification of an APM Server.",
                                            "properties": {
                                                "config": {
                                                    "description": "Config holds the APM Server configuration. See: https://www.elastic.co/guide/en/apm/server/current/configuring-howto-apm-server.html",
                                                    "type": "object",
                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                },
                                                "count": {
                                                    "description": "Count of APM Server instances to deploy.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "elasticsearchRef": {
                                                    "description": "ElasticsearchRef is a reference to the output Elasticsearch cluster running in the same Kubernetes cluster.",
                                                    "properties": {
                                                        "name": {
                                                            "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                            "type": "string",
                                                        },
                                                        "namespace": {
                                                            "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                            "type": "string",
                                                        },
                                                        "secretName": {
                                                            "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                            "type": "string",
                                                        },
                                                        "serviceName": {
                                                            "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                            "type": "string",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "http": {
                                                    "description": "HTTP holds the HTTP layer configuration for the APM Server resource.",
                                                    "properties": {
                                                        "service": {
                                                            "description": "Service defines the template for the associated Kubernetes Service object.",
                                                            "properties": {
                                                                "metadata": {
                                                                    "description": "ObjectMeta is the metadata of the service. The name and namespace provided here are managed by ECK and will be ignored.",
                                                                    "properties": {
                                                                        "annotations": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "finalizers": {
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "labels": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "name": {
                                                                            "type": "string"
                                                                        },
                                                                        "namespace": {
                                                                            "type": "string"
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "spec": {
                                                                    "description": "Spec is the specification of the service.",
                                                                    "properties": {
                                                                        "allocateLoadBalancerNodePorts": {
                                                                            "description": 'allocateLoadBalancerNodePorts defines if NodePorts will be automatically allocated for services with type LoadBalancer.  Default is "true". It may be set to "false" if the cluster load-balancer does not rely on NodePorts.  If the caller requests specific NodePorts (by specifying a value), those requests will be respected, regardless of this field. This field may only be set for services with type LoadBalancer and will be cleared if the type is changed to any other type.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "clusterIP": {
                                                                            "description": 'clusterIP is the IP address of the service and is usually assigned randomly. If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be blank) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address. Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "clusterIPs": {
                                                                            "description": 'ClusterIPs is a list of IP addresses assigned to this service, and are usually assigned randomly.  If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be empty) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address.  Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName.  If this field is not specified, it will be initialized from the clusterIP field.  If this field is specified, clients must ensure that clusterIPs[0] and clusterIP have the same value. \n This field may hold a maximum of two entries (dual-stack IPs, in either order). These IPs must correspond to the values of the ipFamilies field. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "externalIPs": {
                                                                            "description": "externalIPs is a list of IP addresses for which nodes in the cluster will also accept traffic for this service.  These IPs are not managed by Kubernetes.  The user is responsible for ensuring that traffic arrives at a node with this IP.  A common example is external load-balancers that are not part of the Kubernetes system.",
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "externalName": {
                                                                            "description": 'externalName is the external reference that discovery mechanisms will return as an alias for this service (e.g. a DNS CNAME record). No proxying will be involved.  Must be a lowercase RFC-1123 hostname (https://tools.ietf.org/html/rfc1123) and requires `type` to be "ExternalName".',
                                                                            "type": "string",
                                                                        },
                                                                        "externalTrafficPolicy": {
                                                                            "description": 'externalTrafficPolicy describes how nodes distribute service traffic they receive on one of the Service\'s "externally-facing" addresses (NodePorts, ExternalIPs, and LoadBalancer IPs). If set to "Local", the proxy will configure the service in a way that assumes that external load balancers will take care of balancing the service traffic between nodes, and so each node will deliver traffic only to the node-local endpoints of the service, without masquerading the client source IP. (Traffic mistakenly sent to a node with no endpoints will be dropped.) The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features). Note that traffic sent to an External IP or LoadBalancer IP from within the cluster will always get "Cluster" semantics, but clients sending to a NodePort from within the cluster may need to take traffic policy into account when picking a node.',
                                                                            "type": "string",
                                                                        },
                                                                        "healthCheckNodePort": {
                                                                            "description": "healthCheckNodePort specifies the healthcheck nodePort for the service. This only applies when type is set to LoadBalancer and externalTrafficPolicy is set to Local. If a value is specified, is in-range, and is not in use, it will be used.  If not specified, a value will be automatically allocated.  External systems (e.g. load-balancers) can use this port to determine if a given node holds endpoints for this service or not.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type). This field cannot be updated once set.",
                                                                            "format": "int32",
                                                                            "type": "integer",
                                                                        },
                                                                        "internalTrafficPolicy": {
                                                                            "description": 'InternalTrafficPolicy describes how nodes distribute service traffic they receive on the ClusterIP. If set to "Local", the proxy will assume that pods only want to talk to endpoints of the service on the same node as the pod, dropping the traffic if there are no local endpoints. The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features).',
                                                                            "type": "string",
                                                                        },
                                                                        "ipFamilies": {
                                                                            "description": 'IPFamilies is a list of IP families (e.g. IPv4, IPv6) assigned to this service. This field is usually assigned automatically based on cluster configuration and the ipFamilyPolicy field. If this field is specified manually, the requested family is available in the cluster, and ipFamilyPolicy allows it, it will be used; otherwise creation of the service will fail. This field is conditionally mutable: it allows for adding or removing a secondary IP family, but it does not allow changing the primary IP family of the Service. Valid values are "IPv4" and "IPv6".  This field only applies to Services of types ClusterIP, NodePort, and LoadBalancer, and does apply to "headless" services. This field will be wiped when updating a Service to type ExternalName. \n This field may hold a maximum of two entries (dual-stack families, in either order).  These families must correspond to the values of the clusterIPs field, if specified. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field.',
                                                                            "items": {
                                                                                "description": "IPFamily represents the IP Family (IPv4 or IPv6). This type is used to express the family of an IP expressed by a type (e.g. service.spec.ipFamilies).",
                                                                                "type": "string",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "ipFamilyPolicy": {
                                                                            "description": 'IPFamilyPolicy represents the dual-stack-ness requested or required by this Service. If there is no value provided, then this field will be set to SingleStack. Services can be "SingleStack" (a single IP family), "PreferDualStack" (two IP families on dual-stack configured clusters or a single IP family on single-stack clusters), or "RequireDualStack" (two IP families on dual-stack configured clusters, otherwise fail). The ipFamilies and clusterIPs fields depend on the value of this field. This field will be wiped when updating a service to type ExternalName.',
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerClass": {
                                                                            "description": "loadBalancerClass is the class of the load balancer implementation this Service belongs to. If specified, the value of this field must be a label-style identifier, with an optional prefix, e.g. \"internal-vip\" or \"example.com/internal-vip\". Unprefixed names are reserved for end-users. This field can only be set when the Service type is 'LoadBalancer'. If not set, the default load balancer implementation is used, today this is typically done through the cloud provider integration, but should apply for any default implementation. If set, it is assumed that a load balancer implementation is watching for Services with a matching class. Any default load balancer implementation (e.g. cloud providers) should ignore Services that set this field. This field can only be set when creating or updating a Service to type 'LoadBalancer'. Once set, it can not be changed. This field will be wiped when a service is updated to a non 'LoadBalancer' type.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerIP": {
                                                                            "description": "Only applies to Service Type: LoadBalancer. This feature depends on whether the underlying cloud-provider supports specifying the loadBalancerIP when a load balancer is created. This field will be ignored if the cloud-provider does not support the feature. Deprecated: This field was under-specified and its meaning varies across implementations, and it cannot support dual-stack. As of Kubernetes v1.24, users are encouraged to use implementation-specific annotations when available. This field may be removed in a future API version.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerSourceRanges": {
                                                                            "description": 'If specified and supported by the platform, this will restrict traffic through the cloud-provider load-balancer will be restricted to the specified client IPs. This field will be ignored if the cloud-provider does not support the feature." More info: https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "ports": {
                                                                            "description": "The list of ports that are exposed by this service. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies",
                                                                            "items": {
                                                                                "description": "ServicePort contains information on service's port.",
                                                                                "properties": {
                                                                                    "appProtocol": {
                                                                                        "description": "The application protocol for this port. This field follows standard Kubernetes label syntax. Un-prefixed names are reserved for IANA standard service names (as per RFC-6335 and https://www.iana.org/assignments/service-names). Non-standard protocols should use prefixed names such as mycompany.com/my-custom-protocol.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "name": {
                                                                                        "description": "The name of this port within the service. This must be a DNS_LABEL. All ports within a ServiceSpec must have unique names. When considering the endpoints for a Service, this must match the 'name' field in the EndpointPort. Optional if only one ServicePort is defined on this service.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "nodePort": {
                                                                                        "description": "The port on each node on which this service is exposed when type is NodePort or LoadBalancer.  Usually assigned by the system. If a value is specified, in-range, and not in use it will be used, otherwise the operation will fail.  If not specified, a port will be allocated if this Service requires one.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type from NodePort to ClusterIP). More info: https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "port": {
                                                                                        "description": "The port that will be exposed by this service.",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "protocol": {
                                                                                        "default": "TCP",
                                                                                        "description": 'The IP protocol for this port. Supports "TCP", "UDP", and "SCTP". Default is TCP.',
                                                                                        "type": "string",
                                                                                    },
                                                                                    "targetPort": {
                                                                                        "anyOf": [
                                                                                            {
                                                                                                "type": "integer"
                                                                                            },
                                                                                            {
                                                                                                "type": "string"
                                                                                            },
                                                                                        ],
                                                                                        "description": "Number or name of the port to access on the pods targeted by the service. Number must be in the range 1 to 65535. Name must be an IANA_SVC_NAME. If this is a string, it will be looked up as a named port in the target Pod's container ports. If this is not specified, the value of the 'port' field is used (an identity map). This field is ignored for services with clusterIP=None, and should be omitted or set equal to the 'port' field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#defining-a-service",
                                                                                        "x-kubernetes-int-or-string": True,
                                                                                    },
                                                                                },
                                                                                "required": [
                                                                                    "port"
                                                                                ],
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-map-keys": [
                                                                                "port",
                                                                                "protocol",
                                                                            ],
                                                                            "x-kubernetes-list-type": "map",
                                                                        },
                                                                        "publishNotReadyAddresses": {
                                                                            "description": 'publishNotReadyAddresses indicates that any agent which deals with endpoints for this Service should disregard any indications of ready/not-ready. The primary use case for setting this field is for a StatefulSet\'s Headless Service to propagate SRV DNS records for its Pods for the purpose of peer discovery. The Kubernetes controllers that generate Endpoints and EndpointSlice resources for Services interpret this to mean that all endpoints are considered "ready" even if the Pods themselves are not. Agents which consume only Kubernetes generated endpoints through the Endpoints or EndpointSlice resources can safely assume this behavior.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "selector": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "description": "Route service traffic to pods with label keys and values matching this selector. If empty or not present, the service is assumed to have an external process managing its endpoints, which Kubernetes will not modify. Only applies to types ClusterIP, NodePort, and LoadBalancer. Ignored if type is ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/",
                                                                            "type": "object",
                                                                            "x-kubernetes-map-type": "atomic",
                                                                        },
                                                                        "sessionAffinity": {
                                                                            "description": 'Supports "ClientIP" and "None". Used to maintain session affinity. Enable client IP based session affinity. Must be ClientIP or None. Defaults to None. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "sessionAffinityConfig": {
                                                                            "description": "sessionAffinityConfig contains the configurations of session affinity.",
                                                                            "properties": {
                                                                                "clientIP": {
                                                                                    "description": "clientIP contains the configurations of Client IP based session affinity.",
                                                                                    "properties": {
                                                                                        "timeoutSeconds": {
                                                                                            "description": 'timeoutSeconds specifies the seconds of ClientIP type session sticky time. The value must be >0 && <=86400(for 1 day) if ServiceAffinity == "ClientIP". Default value is 10800(for 3 hours).',
                                                                                            "format": "int32",
                                                                                            "type": "integer",
                                                                                        }
                                                                                    },
                                                                                    "type": "object",
                                                                                }
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "type": {
                                                                            "description": 'type determines how the Service is exposed. Defaults to ClusterIP. Valid options are ExternalName, ClusterIP, NodePort, and LoadBalancer. "ClusterIP" allocates a cluster-internal IP address for load-balancing to endpoints. Endpoints are determined by the selector or if that is not specified, by manual construction of an Endpoints object or EndpointSlice objects. If clusterIP is "None", no virtual IP is allocated and the endpoints are published as a set of endpoints rather than a virtual IP. "NodePort" builds on ClusterIP and allocates a port on every node which routes to the same endpoints as the clusterIP. "LoadBalancer" builds on NodePort and creates an external load-balancer (if supported in the current cloud) which routes to the same endpoints as the clusterIP. "ExternalName" aliases this service to the specified externalName. Several other fields do not apply to ExternalName services. More info: https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                        "tls": {
                                                            "description": "TLS defines options for configuring TLS for HTTP.",
                                                            "properties": {
                                                                "certificate": {
                                                                    "description": "Certificate is a reference to a Kubernetes secret that contains the certificate and private key for enabling TLS. The referenced secret should contain the following: \n - `ca.crt`: The certificate authority (optional). - `tls.crt`: The certificate (or a chain). - `tls.key`: The private key to the first certificate in the certificate chain.",
                                                                    "properties": {
                                                                        "secretName": {
                                                                            "description": "SecretName is the name of the secret.",
                                                                            "type": "string",
                                                                        }
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "selfSignedCertificate": {
                                                                    "description": "SelfSignedCertificate allows configuring the self-signed certificate generated by the operator.",
                                                                    "properties": {
                                                                        "disabled": {
                                                                            "description": "Disabled indicates that the provisioning of the self-signed certifcate should be disabled.",
                                                                            "type": "boolean",
                                                                        },
                                                                        "subjectAltNames": {
                                                                            "description": "SubjectAlternativeNames is a list of SANs to include in the generated HTTP TLS certificate.",
                                                                            "items": {
                                                                                "description": "SubjectAlternativeName represents a SAN entry in a x509 certificate.",
                                                                                "properties": {
                                                                                    "dns": {
                                                                                        "description": "DNS is the DNS name of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "ip": {
                                                                                        "description": "IP is the IP address of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                },
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "image": {
                                                    "description": "Image is the APM Server Docker image to deploy.",
                                                    "type": "string",
                                                },
                                                "kibanaRef": {
                                                    "description": "KibanaRef is a reference to a Kibana instance running in the same Kubernetes cluster. It allows APM agent central configuration management in Kibana.",
                                                    "properties": {
                                                        "name": {
                                                            "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                            "type": "string",
                                                        },
                                                        "namespace": {
                                                            "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                            "type": "string",
                                                        },
                                                        "secretName": {
                                                            "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                            "type": "string",
                                                        },
                                                        "serviceName": {
                                                            "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                            "type": "string",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "podTemplate": {
                                                    "description": "PodTemplate provides customisation options (labels, annotations, affinity rules, resource requests, and so on) for the APM Server pods.",
                                                    "type": "object",
                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                },
                                                "revisionHistoryLimit": {
                                                    "description": "RevisionHistoryLimit is the number of revisions to retain to allow rollback in the underlying Deployment.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "secureSettings": {
                                                    "description": "SecureSettings is a list of references to Kubernetes secrets containing sensitive configuration options for APM Server.",
                                                    "items": {
                                                        "description": "SecretSource defines a data source based on a Kubernetes Secret.",
                                                        "properties": {
                                                            "entries": {
                                                                "description": "Entries define how to project each key-value pair in the secret to filesystem paths. If not defined, all keys will be projected to similarly named paths in the filesystem. If defined, only the specified keys will be projected to the corresponding paths.",
                                                                "items": {
                                                                    "description": "KeyToPath defines how to map a key in a Secret object to a filesystem path.",
                                                                    "properties": {
                                                                        "key": {
                                                                            "description": "Key is the key contained in the secret.",
                                                                            "type": "string",
                                                                        },
                                                                        "path": {
                                                                            "description": 'Path is the relative file path to map the key to. Path must not be an absolute file path and must not contain any ".." components.',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "required": ["key"],
                                                                    "type": "object",
                                                                },
                                                                "type": "array",
                                                            },
                                                            "secretName": {
                                                                "description": "SecretName is the name of the secret.",
                                                                "type": "string",
                                                            },
                                                        },
                                                        "required": ["secretName"],
                                                        "type": "object",
                                                    },
                                                    "type": "array",
                                                },
                                                "serviceAccountName": {
                                                    "description": "ServiceAccountName is used to check access from the current resource to a resource (for ex. Elasticsearch) in a different namespace. Can only be used if ECK is enforcing RBAC on references.",
                                                    "type": "string",
                                                },
                                                "version": {
                                                    "description": "Version of the APM Server.",
                                                    "type": "string",
                                                },
                                            },
                                            "required": ["version"],
                                            "type": "object",
                                        },
                                        "status": {
                                            "description": "ApmServerStatus defines the observed state of ApmServer",
                                            "properties": {
                                                "availableNodes": {
                                                    "description": "AvailableNodes is the number of available replicas in the deployment.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "count": {
                                                    "description": "Count corresponds to Scale.Status.Replicas, which is the actual number of observed instances of the scaled object.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "elasticsearchAssociationStatus": {
                                                    "description": "ElasticsearchAssociationStatus is the status of any auto-linking to Elasticsearch clusters.",
                                                    "type": "string",
                                                },
                                                "health": {
                                                    "description": "Health of the deployment.",
                                                    "type": "string",
                                                },
                                                "kibanaAssociationStatus": {
                                                    "description": "KibanaAssociationStatus is the status of any auto-linking to Kibana.",
                                                    "type": "string",
                                                },
                                                "observedGeneration": {
                                                    "description": "ObservedGeneration represents the .metadata.generation that the status is based upon. It corresponds to the metadata generation, which is updated on mutation by the API Server. If the generation observed in status diverges from the generation in metadata, the APM Server controller has not yet processed the changes contained in the APM Server specification.",
                                                    "format": "int64",
                                                    "type": "integer",
                                                },
                                                "secretTokenSecret": {
                                                    "description": "SecretTokenSecretName is the name of the Secret that contains the secret token",
                                                    "type": "string",
                                                },
                                                "selector": {
                                                    "description": "Selector is the label selector used to find all pods.",
                                                    "type": "string",
                                                },
                                                "service": {
                                                    "description": "ExternalService is the name of the service the agents should connect to.",
                                                    "type": "string",
                                                },
                                                "version": {
                                                    "description": "Version of the stack resource currently running. During version upgrades, multiple versions may run in parallel: this value specifies the lowest version currently running.",
                                                    "type": "string",
                                                },
                                            },
                                            "type": "object",
                                        },
                                    },
                                    "type": "object",
                                }
                            },
                            "served": True,
                            "storage": True,
                            "subresources": {
                                "scale": {
                                    "labelSelectorPath": ".status.selector",
                                    "specReplicasPath": ".spec.count",
                                    "statusReplicasPath": ".status.count",
                                },
                                "status": {},
                            },
                        },
                        {
                            "additionalPrinterColumns": [
                                {
                                    "jsonPath": ".status.health",
                                    "name": "health",
                                    "type": "string",
                                },
                                {
                                    "description": "Available nodes",
                                    "jsonPath": ".status.availableNodes",
                                    "name": "nodes",
                                    "type": "integer",
                                },
                                {
                                    "description": "APM version",
                                    "jsonPath": ".spec.version",
                                    "name": "version",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".metadata.creationTimestamp",
                                    "name": "age",
                                    "type": "date",
                                },
                            ],
                            "name": "v1beta1",
                            "schema": {
                                "openAPIV3Schema": {
                                    "description": "ApmServer represents an APM Server resource in a Kubernetes cluster.",
                                    "properties": {
                                        "apiVersion": {
                                            "description": "APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources",
                                            "type": "string",
                                        },
                                        "kind": {
                                            "description": "Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds",
                                            "type": "string",
                                        },
                                        "metadata": {"type": "object"},
                                        "spec": {
                                            "description": "ApmServerSpec holds the specification of an APM Server.",
                                            "properties": {
                                                "config": {
                                                    "description": "Config holds the APM Server configuration. See: https://www.elastic.co/guide/en/apm/server/current/configuring-howto-apm-server.html",
                                                    "type": "object",
                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                },
                                                "count": {
                                                    "description": "Count of APM Server instances to deploy.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "elasticsearchRef": {
                                                    "description": "ElasticsearchRef is a reference to the output Elasticsearch cluster running in the same Kubernetes cluster.",
                                                    "properties": {
                                                        "name": {
                                                            "description": "Name of the Kubernetes object.",
                                                            "type": "string",
                                                        },
                                                        "namespace": {
                                                            "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                            "type": "string",
                                                        },
                                                    },
                                                    "required": ["name"],
                                                    "type": "object",
                                                },
                                                "http": {
                                                    "description": "HTTP holds the HTTP layer configuration for the APM Server resource.",
                                                    "properties": {
                                                        "service": {
                                                            "description": "Service defines the template for the associated Kubernetes Service object.",
                                                            "properties": {
                                                                "metadata": {
                                                                    "description": "ObjectMeta is the metadata of the service. The name and namespace provided here are managed by ECK and will be ignored.",
                                                                    "properties": {
                                                                        "annotations": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "finalizers": {
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "labels": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "name": {
                                                                            "type": "string"
                                                                        },
                                                                        "namespace": {
                                                                            "type": "string"
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "spec": {
                                                                    "description": "Spec is the specification of the service.",
                                                                    "properties": {
                                                                        "allocateLoadBalancerNodePorts": {
                                                                            "description": 'allocateLoadBalancerNodePorts defines if NodePorts will be automatically allocated for services with type LoadBalancer.  Default is "true". It may be set to "false" if the cluster load-balancer does not rely on NodePorts.  If the caller requests specific NodePorts (by specifying a value), those requests will be respected, regardless of this field. This field may only be set for services with type LoadBalancer and will be cleared if the type is changed to any other type.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "clusterIP": {
                                                                            "description": 'clusterIP is the IP address of the service and is usually assigned randomly. If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be blank) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address. Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "clusterIPs": {
                                                                            "description": 'ClusterIPs is a list of IP addresses assigned to this service, and are usually assigned randomly.  If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be empty) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address.  Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName.  If this field is not specified, it will be initialized from the clusterIP field.  If this field is specified, clients must ensure that clusterIPs[0] and clusterIP have the same value. \n This field may hold a maximum of two entries (dual-stack IPs, in either order). These IPs must correspond to the values of the ipFamilies field. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "externalIPs": {
                                                                            "description": "externalIPs is a list of IP addresses for which nodes in the cluster will also accept traffic for this service.  These IPs are not managed by Kubernetes.  The user is responsible for ensuring that traffic arrives at a node with this IP.  A common example is external load-balancers that are not part of the Kubernetes system.",
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "externalName": {
                                                                            "description": 'externalName is the external reference that discovery mechanisms will return as an alias for this service (e.g. a DNS CNAME record). No proxying will be involved.  Must be a lowercase RFC-1123 hostname (https://tools.ietf.org/html/rfc1123) and requires `type` to be "ExternalName".',
                                                                            "type": "string",
                                                                        },
                                                                        "externalTrafficPolicy": {
                                                                            "description": 'externalTrafficPolicy describes how nodes distribute service traffic they receive on one of the Service\'s "externally-facing" addresses (NodePorts, ExternalIPs, and LoadBalancer IPs). If set to "Local", the proxy will configure the service in a way that assumes that external load balancers will take care of balancing the service traffic between nodes, and so each node will deliver traffic only to the node-local endpoints of the service, without masquerading the client source IP. (Traffic mistakenly sent to a node with no endpoints will be dropped.) The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features). Note that traffic sent to an External IP or LoadBalancer IP from within the cluster will always get "Cluster" semantics, but clients sending to a NodePort from within the cluster may need to take traffic policy into account when picking a node.',
                                                                            "type": "string",
                                                                        },
                                                                        "healthCheckNodePort": {
                                                                            "description": "healthCheckNodePort specifies the healthcheck nodePort for the service. This only applies when type is set to LoadBalancer and externalTrafficPolicy is set to Local. If a value is specified, is in-range, and is not in use, it will be used.  If not specified, a value will be automatically allocated.  External systems (e.g. load-balancers) can use this port to determine if a given node holds endpoints for this service or not.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type). This field cannot be updated once set.",
                                                                            "format": "int32",
                                                                            "type": "integer",
                                                                        },
                                                                        "internalTrafficPolicy": {
                                                                            "description": 'InternalTrafficPolicy describes how nodes distribute service traffic they receive on the ClusterIP. If set to "Local", the proxy will assume that pods only want to talk to endpoints of the service on the same node as the pod, dropping the traffic if there are no local endpoints. The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features).',
                                                                            "type": "string",
                                                                        },
                                                                        "ipFamilies": {
                                                                            "description": 'IPFamilies is a list of IP families (e.g. IPv4, IPv6) assigned to this service. This field is usually assigned automatically based on cluster configuration and the ipFamilyPolicy field. If this field is specified manually, the requested family is available in the cluster, and ipFamilyPolicy allows it, it will be used; otherwise creation of the service will fail. This field is conditionally mutable: it allows for adding or removing a secondary IP family, but it does not allow changing the primary IP family of the Service. Valid values are "IPv4" and "IPv6".  This field only applies to Services of types ClusterIP, NodePort, and LoadBalancer, and does apply to "headless" services. This field will be wiped when updating a Service to type ExternalName. \n This field may hold a maximum of two entries (dual-stack families, in either order).  These families must correspond to the values of the clusterIPs field, if specified. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field.',
                                                                            "items": {
                                                                                "description": "IPFamily represents the IP Family (IPv4 or IPv6). This type is used to express the family of an IP expressed by a type (e.g. service.spec.ipFamilies).",
                                                                                "type": "string",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "ipFamilyPolicy": {
                                                                            "description": 'IPFamilyPolicy represents the dual-stack-ness requested or required by this Service. If there is no value provided, then this field will be set to SingleStack. Services can be "SingleStack" (a single IP family), "PreferDualStack" (two IP families on dual-stack configured clusters or a single IP family on single-stack clusters), or "RequireDualStack" (two IP families on dual-stack configured clusters, otherwise fail). The ipFamilies and clusterIPs fields depend on the value of this field. This field will be wiped when updating a service to type ExternalName.',
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerClass": {
                                                                            "description": "loadBalancerClass is the class of the load balancer implementation this Service belongs to. If specified, the value of this field must be a label-style identifier, with an optional prefix, e.g. \"internal-vip\" or \"example.com/internal-vip\". Unprefixed names are reserved for end-users. This field can only be set when the Service type is 'LoadBalancer'. If not set, the default load balancer implementation is used, today this is typically done through the cloud provider integration, but should apply for any default implementation. If set, it is assumed that a load balancer implementation is watching for Services with a matching class. Any default load balancer implementation (e.g. cloud providers) should ignore Services that set this field. This field can only be set when creating or updating a Service to type 'LoadBalancer'. Once set, it can not be changed. This field will be wiped when a service is updated to a non 'LoadBalancer' type.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerIP": {
                                                                            "description": "Only applies to Service Type: LoadBalancer. This feature depends on whether the underlying cloud-provider supports specifying the loadBalancerIP when a load balancer is created. This field will be ignored if the cloud-provider does not support the feature. Deprecated: This field was under-specified and its meaning varies across implementations, and it cannot support dual-stack. As of Kubernetes v1.24, users are encouraged to use implementation-specific annotations when available. This field may be removed in a future API version.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerSourceRanges": {
                                                                            "description": 'If specified and supported by the platform, this will restrict traffic through the cloud-provider load-balancer will be restricted to the specified client IPs. This field will be ignored if the cloud-provider does not support the feature." More info: https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "ports": {
                                                                            "description": "The list of ports that are exposed by this service. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies",
                                                                            "items": {
                                                                                "description": "ServicePort contains information on service's port.",
                                                                                "properties": {
                                                                                    "appProtocol": {
                                                                                        "description": "The application protocol for this port. This field follows standard Kubernetes label syntax. Un-prefixed names are reserved for IANA standard service names (as per RFC-6335 and https://www.iana.org/assignments/service-names). Non-standard protocols should use prefixed names such as mycompany.com/my-custom-protocol.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "name": {
                                                                                        "description": "The name of this port within the service. This must be a DNS_LABEL. All ports within a ServiceSpec must have unique names. When considering the endpoints for a Service, this must match the 'name' field in the EndpointPort. Optional if only one ServicePort is defined on this service.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "nodePort": {
                                                                                        "description": "The port on each node on which this service is exposed when type is NodePort or LoadBalancer.  Usually assigned by the system. If a value is specified, in-range, and not in use it will be used, otherwise the operation will fail.  If not specified, a port will be allocated if this Service requires one.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type from NodePort to ClusterIP). More info: https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "port": {
                                                                                        "description": "The port that will be exposed by this service.",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "protocol": {
                                                                                        "default": "TCP",
                                                                                        "description": 'The IP protocol for this port. Supports "TCP", "UDP", and "SCTP". Default is TCP.',
                                                                                        "type": "string",
                                                                                    },
                                                                                    "targetPort": {
                                                                                        "anyOf": [
                                                                                            {
                                                                                                "type": "integer"
                                                                                            },
                                                                                            {
                                                                                                "type": "string"
                                                                                            },
                                                                                        ],
                                                                                        "description": "Number or name of the port to access on the pods targeted by the service. Number must be in the range 1 to 65535. Name must be an IANA_SVC_NAME. If this is a string, it will be looked up as a named port in the target Pod's container ports. If this is not specified, the value of the 'port' field is used (an identity map). This field is ignored for services with clusterIP=None, and should be omitted or set equal to the 'port' field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#defining-a-service",
                                                                                        "x-kubernetes-int-or-string": True,
                                                                                    },
                                                                                },
                                                                                "required": [
                                                                                    "port"
                                                                                ],
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-map-keys": [
                                                                                "port",
                                                                                "protocol",
                                                                            ],
                                                                            "x-kubernetes-list-type": "map",
                                                                        },
                                                                        "publishNotReadyAddresses": {
                                                                            "description": 'publishNotReadyAddresses indicates that any agent which deals with endpoints for this Service should disregard any indications of ready/not-ready. The primary use case for setting this field is for a StatefulSet\'s Headless Service to propagate SRV DNS records for its Pods for the purpose of peer discovery. The Kubernetes controllers that generate Endpoints and EndpointSlice resources for Services interpret this to mean that all endpoints are considered "ready" even if the Pods themselves are not. Agents which consume only Kubernetes generated endpoints through the Endpoints or EndpointSlice resources can safely assume this behavior.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "selector": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "description": "Route service traffic to pods with label keys and values matching this selector. If empty or not present, the service is assumed to have an external process managing its endpoints, which Kubernetes will not modify. Only applies to types ClusterIP, NodePort, and LoadBalancer. Ignored if type is ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/",
                                                                            "type": "object",
                                                                            "x-kubernetes-map-type": "atomic",
                                                                        },
                                                                        "sessionAffinity": {
                                                                            "description": 'Supports "ClientIP" and "None". Used to maintain session affinity. Enable client IP based session affinity. Must be ClientIP or None. Defaults to None. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "sessionAffinityConfig": {
                                                                            "description": "sessionAffinityConfig contains the configurations of session affinity.",
                                                                            "properties": {
                                                                                "clientIP": {
                                                                                    "description": "clientIP contains the configurations of Client IP based session affinity.",
                                                                                    "properties": {
                                                                                        "timeoutSeconds": {
                                                                                            "description": 'timeoutSeconds specifies the seconds of ClientIP type session sticky time. The value must be >0 && <=86400(for 1 day) if ServiceAffinity == "ClientIP". Default value is 10800(for 3 hours).',
                                                                                            "format": "int32",
                                                                                            "type": "integer",
                                                                                        }
                                                                                    },
                                                                                    "type": "object",
                                                                                }
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "type": {
                                                                            "description": 'type determines how the Service is exposed. Defaults to ClusterIP. Valid options are ExternalName, ClusterIP, NodePort, and LoadBalancer. "ClusterIP" allocates a cluster-internal IP address for load-balancing to endpoints. Endpoints are determined by the selector or if that is not specified, by manual construction of an Endpoints object or EndpointSlice objects. If clusterIP is "None", no virtual IP is allocated and the endpoints are published as a set of endpoints rather than a virtual IP. "NodePort" builds on ClusterIP and allocates a port on every node which routes to the same endpoints as the clusterIP. "LoadBalancer" builds on NodePort and creates an external load-balancer (if supported in the current cloud) which routes to the same endpoints as the clusterIP. "ExternalName" aliases this service to the specified externalName. Several other fields do not apply to ExternalName services. More info: https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                        "tls": {
                                                            "description": "TLS defines options for configuring TLS for HTTP.",
                                                            "properties": {
                                                                "certificate": {
                                                                    "description": "Certificate is a reference to a Kubernetes secret that contains the certificate and private key for enabling TLS. The referenced secret should contain the following: \n - `ca.crt`: The certificate authority (optional). - `tls.crt`: The certificate (or a chain). - `tls.key`: The private key to the first certificate in the certificate chain.",
                                                                    "properties": {
                                                                        "secretName": {
                                                                            "description": "SecretName is the name of the secret.",
                                                                            "type": "string",
                                                                        }
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "selfSignedCertificate": {
                                                                    "description": "SelfSignedCertificate allows configuring the self-signed certificate generated by the operator.",
                                                                    "properties": {
                                                                        "disabled": {
                                                                            "description": "Disabled indicates that the provisioning of the self-signed certifcate should be disabled.",
                                                                            "type": "boolean",
                                                                        },
                                                                        "subjectAltNames": {
                                                                            "description": "SubjectAlternativeNames is a list of SANs to include in the generated HTTP TLS certificate.",
                                                                            "items": {
                                                                                "description": "SubjectAlternativeName represents a SAN entry in a x509 certificate.",
                                                                                "properties": {
                                                                                    "dns": {
                                                                                        "description": "DNS is the DNS name of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "ip": {
                                                                                        "description": "IP is the IP address of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                },
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "image": {
                                                    "description": "Image is the APM Server Docker image to deploy.",
                                                    "type": "string",
                                                },
                                                "podTemplate": {
                                                    "description": "PodTemplate provides customisation options (labels, annotations, affinity rules, resource requests, and so on) for the APM Server pods.",
                                                    "type": "object",
                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                },
                                                "secureSettings": {
                                                    "description": "SecureSettings is a list of references to Kubernetes secrets containing sensitive configuration options for APM Server.",
                                                    "items": {
                                                        "description": "SecretSource defines a data source based on a Kubernetes Secret.",
                                                        "properties": {
                                                            "entries": {
                                                                "description": "Entries define how to project each key-value pair in the secret to filesystem paths. If not defined, all keys will be projected to similarly named paths in the filesystem. If defined, only the specified keys will be projected to the corresponding paths.",
                                                                "items": {
                                                                    "description": "KeyToPath defines how to map a key in a Secret object to a filesystem path.",
                                                                    "properties": {
                                                                        "key": {
                                                                            "description": "Key is the key contained in the secret.",
                                                                            "type": "string",
                                                                        },
                                                                        "path": {
                                                                            "description": 'Path is the relative file path to map the key to. Path must not be an absolute file path and must not contain any ".." components.',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "required": ["key"],
                                                                    "type": "object",
                                                                },
                                                                "type": "array",
                                                            },
                                                            "secretName": {
                                                                "description": "SecretName is the name of the secret.",
                                                                "type": "string",
                                                            },
                                                        },
                                                        "required": ["secretName"],
                                                        "type": "object",
                                                    },
                                                    "type": "array",
                                                },
                                                "version": {
                                                    "description": "Version of the APM Server.",
                                                    "type": "string",
                                                },
                                            },
                                            "type": "object",
                                        },
                                        "status": {
                                            "description": "ApmServerStatus defines the observed state of ApmServer",
                                            "properties": {
                                                "associationStatus": {
                                                    "description": "Association is the status of any auto-linking to Elasticsearch clusters.",
                                                    "type": "string",
                                                },
                                                "availableNodes": {
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "health": {
                                                    "description": "ApmServerHealth expresses the status of the Apm Server instances.",
                                                    "type": "string",
                                                },
                                                "secretTokenSecret": {
                                                    "description": "SecretTokenSecretName is the name of the Secret that contains the secret token",
                                                    "type": "string",
                                                },
                                                "service": {
                                                    "description": "ExternalService is the name of the service the agents should connect to.",
                                                    "type": "string",
                                                },
                                            },
                                            "type": "object",
                                        },
                                    },
                                    "type": "object",
                                }
                            },
                            "served": True,
                            "storage": False,
                            "subresources": {"status": {}},
                        },
                        {
                            "name": "v1alpha1",
                            "schema": {
                                "openAPIV3Schema": {
                                    "description": "to not break compatibility when upgrading from previous versions of the CRD",
                                    "type": "object",
                                }
                            },
                            "served": False,
                            "storage": False,
                        },
                    ],
                },
            },
            {
                "apiVersion": "apiextensions.k8s.io/v1",
                "kind": "CustomResourceDefinition",
                "metadata": {
                    "annotations": {"controller-gen.kubebuilder.io/version": "v0.10.0"},
                    "creationTimestamp": None,
                    "labels": {
                        "app.kubernetes.io/instance": "elastic-operator",
                        "app.kubernetes.io/name": "eck-operator-crds",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                    "name": "beats.beat.k8s.elastic.co",
                },
                "spec": {
                    "group": "beat.k8s.elastic.co",
                    "names": {
                        "categories": ["elastic"],
                        "kind": "Beat",
                        "listKind": "BeatList",
                        "plural": "beats",
                        "shortNames": ["beat"],
                        "singular": "beat",
                    },
                    "scope": "Namespaced",
                    "versions": [
                        {
                            "additionalPrinterColumns": [
                                {
                                    "jsonPath": ".status.health",
                                    "name": "health",
                                    "type": "string",
                                },
                                {
                                    "description": "Available nodes",
                                    "jsonPath": ".status.availableNodes",
                                    "name": "available",
                                    "type": "integer",
                                },
                                {
                                    "description": "Expected nodes",
                                    "jsonPath": ".status.expectedNodes",
                                    "name": "expected",
                                    "type": "integer",
                                },
                                {
                                    "description": "Beat type",
                                    "jsonPath": ".spec.type",
                                    "name": "type",
                                    "type": "string",
                                },
                                {
                                    "description": "Beat version",
                                    "jsonPath": ".status.version",
                                    "name": "version",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".metadata.creationTimestamp",
                                    "name": "age",
                                    "type": "date",
                                },
                            ],
                            "name": "v1beta1",
                            "schema": {
                                "openAPIV3Schema": {
                                    "description": "Beat is the Schema for the Beats API.",
                                    "properties": {
                                        "apiVersion": {
                                            "description": "APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources",
                                            "type": "string",
                                        },
                                        "kind": {
                                            "description": "Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds",
                                            "type": "string",
                                        },
                                        "metadata": {"type": "object"},
                                        "spec": {
                                            "description": "BeatSpec defines the desired state of a Beat.",
                                            "properties": {
                                                "config": {
                                                    "description": "Config holds the Beat configuration. At most one of [`Config`, `ConfigRef`] can be specified.",
                                                    "type": "object",
                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                },
                                                "configRef": {
                                                    "description": 'ConfigRef contains a reference to an existing Kubernetes Secret holding the Beat configuration. Beat settings must be specified as yaml, under a single "beat.yml" entry. At most one of [`Config`, `ConfigRef`] can be specified.',
                                                    "properties": {
                                                        "secretName": {
                                                            "description": "SecretName is the name of the secret.",
                                                            "type": "string",
                                                        }
                                                    },
                                                    "type": "object",
                                                },
                                                "daemonSet": {
                                                    "description": "DaemonSet specifies the Beat should be deployed as a DaemonSet, and allows providing its spec. Cannot be used along with `deployment`. If both are absent a default for the Type is used.",
                                                    "properties": {
                                                        "podTemplate": {
                                                            "description": "PodTemplateSpec describes the data a pod should have when created from a template",
                                                            "type": "object",
                                                            "x-kubernetes-preserve-unknown-fields": True,
                                                        },
                                                        "updateStrategy": {
                                                            "description": "DaemonSetUpdateStrategy is a struct used to control the update strategy for a DaemonSet.",
                                                            "properties": {
                                                                "rollingUpdate": {
                                                                    "description": 'Rolling update config params. Present only if type = "RollingUpdate". --- TODO: Update this to follow our convention for oneOf, whatever we decide it to be. Same as Deployment `strategy.rollingUpdate`. See https://github.com/kubernetes/kubernetes/issues/35345',
                                                                    "properties": {
                                                                        "maxSurge": {
                                                                            "anyOf": [
                                                                                {
                                                                                    "type": "integer"
                                                                                },
                                                                                {
                                                                                    "type": "string"
                                                                                },
                                                                            ],
                                                                            "description": "The maximum number of nodes with an existing available DaemonSet pod that can have an updated DaemonSet pod during during an update. Value can be an absolute number (ex: 5) or a percentage of desired pods (ex: 10%). This can not be 0 if MaxUnavailable is 0. Absolute number is calculated from percentage by rounding up to a minimum of 1. Default value is 0. Example: when this is set to 30%, at most 30% of the total number of nodes that should be running the daemon pod (i.e. status.desiredNumberScheduled) can have their a new pod created before the old pod is marked as deleted. The update starts by launching new pods on 30% of nodes. Once an updated pod is available (Ready for at least minReadySeconds) the old DaemonSet pod on that node is marked deleted. If the old pod becomes unavailable for any reason (Ready transitions to false, is evicted, or is drained) an updated pod is immediatedly created on that node without considering surge limits. Allowing surge implies the possibility that the resources consumed by the daemonset on any given node can double if the readiness check fails, and so resource intensive daemonsets should take into account that they may cause evictions during disruption.",
                                                                            "x-kubernetes-int-or-string": True,
                                                                        },
                                                                        "maxUnavailable": {
                                                                            "anyOf": [
                                                                                {
                                                                                    "type": "integer"
                                                                                },
                                                                                {
                                                                                    "type": "string"
                                                                                },
                                                                            ],
                                                                            "description": "The maximum number of DaemonSet pods that can be unavailable during the update. Value can be an absolute number (ex: 5) or a percentage of total number of DaemonSet pods at the start of the update (ex: 10%). Absolute number is calculated from percentage by rounding up. This cannot be 0 if MaxSurge is 0 Default value is 1. Example: when this is set to 30%, at most 30% of the total number of nodes that should be running the daemon pod (i.e. status.desiredNumberScheduled) can have their pods stopped for an update at any given time. The update starts by stopping at most 30% of those DaemonSet pods and then brings up new DaemonSet pods in their place. Once the new pods are available, it then proceeds onto other DaemonSet pods, thus ensuring that at least 70% of original number of DaemonSet pods are available at all times during the update.",
                                                                            "x-kubernetes-int-or-string": True,
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "type": {
                                                                    "description": 'Type of daemon set update. Can be "RollingUpdate" or "OnDelete". Default is RollingUpdate.',
                                                                    "type": "string",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "deployment": {
                                                    "description": "Deployment specifies the Beat should be deployed as a Deployment, and allows providing its spec. Cannot be used along with `daemonSet`. If both are absent a default for the Type is used.",
                                                    "properties": {
                                                        "podTemplate": {
                                                            "description": "PodTemplateSpec describes the data a pod should have when created from a template",
                                                            "type": "object",
                                                            "x-kubernetes-preserve-unknown-fields": True,
                                                        },
                                                        "replicas": {
                                                            "format": "int32",
                                                            "type": "integer",
                                                        },
                                                        "strategy": {
                                                            "description": "DeploymentStrategy describes how to replace existing pods with new ones.",
                                                            "properties": {
                                                                "rollingUpdate": {
                                                                    "description": "Rolling update config params. Present only if DeploymentStrategyType = RollingUpdate. --- TODO: Update this to follow our convention for oneOf, whatever we decide it to be.",
                                                                    "properties": {
                                                                        "maxSurge": {
                                                                            "anyOf": [
                                                                                {
                                                                                    "type": "integer"
                                                                                },
                                                                                {
                                                                                    "type": "string"
                                                                                },
                                                                            ],
                                                                            "description": "The maximum number of pods that can be scheduled above the desired number of pods. Value can be an absolute number (ex: 5) or a percentage of desired pods (ex: 10%). This can not be 0 if MaxUnavailable is 0. Absolute number is calculated from percentage by rounding up. Defaults to 25%. Example: when this is set to 30%, the new ReplicaSet can be scaled up immediately when the rolling update starts, such that the total number of old and new pods do not exceed 130% of desired pods. Once old pods have been killed, new ReplicaSet can be scaled up further, ensuring that total number of pods running at any time during the update is at most 130% of desired pods.",
                                                                            "x-kubernetes-int-or-string": True,
                                                                        },
                                                                        "maxUnavailable": {
                                                                            "anyOf": [
                                                                                {
                                                                                    "type": "integer"
                                                                                },
                                                                                {
                                                                                    "type": "string"
                                                                                },
                                                                            ],
                                                                            "description": "The maximum number of pods that can be unavailable during the update. Value can be an absolute number (ex: 5) or a percentage of desired pods (ex: 10%). Absolute number is calculated from percentage by rounding down. This can not be 0 if MaxSurge is 0. Defaults to 25%. Example: when this is set to 30%, the old ReplicaSet can be scaled down to 70% of desired pods immediately when the rolling update starts. Once new pods are ready, old ReplicaSet can be scaled down further, followed by scaling up the new ReplicaSet, ensuring that the total number of pods available at all times during the update is at least 70% of desired pods.",
                                                                            "x-kubernetes-int-or-string": True,
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "type": {
                                                                    "description": 'Type of deployment. Can be "Recreate" or "RollingUpdate". Default is RollingUpdate.',
                                                                    "type": "string",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "elasticsearchRef": {
                                                    "description": "ElasticsearchRef is a reference to an Elasticsearch cluster running in the same Kubernetes cluster.",
                                                    "properties": {
                                                        "name": {
                                                            "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                            "type": "string",
                                                        },
                                                        "namespace": {
                                                            "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                            "type": "string",
                                                        },
                                                        "secretName": {
                                                            "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                            "type": "string",
                                                        },
                                                        "serviceName": {
                                                            "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                            "type": "string",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "image": {
                                                    "description": "Image is the Beat Docker image to deploy. Version and Type have to match the Beat in the image.",
                                                    "type": "string",
                                                },
                                                "kibanaRef": {
                                                    "description": "KibanaRef is a reference to a Kibana instance running in the same Kubernetes cluster. It allows automatic setup of dashboards and visualizations.",
                                                    "properties": {
                                                        "name": {
                                                            "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                            "type": "string",
                                                        },
                                                        "namespace": {
                                                            "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                            "type": "string",
                                                        },
                                                        "secretName": {
                                                            "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                            "type": "string",
                                                        },
                                                        "serviceName": {
                                                            "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                            "type": "string",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "monitoring": {
                                                    "description": "Monitoring enables you to collect and ship logs and metrics for this Beat. Metricbeat and/or Filebeat sidecars are configured and send monitoring data to an Elasticsearch monitoring cluster running in the same Kubernetes cluster.",
                                                    "properties": {
                                                        "logs": {
                                                            "description": "Logs holds references to Elasticsearch clusters which receive log data from an associated resource.",
                                                            "properties": {
                                                                "elasticsearchRefs": {
                                                                    "description": "ElasticsearchRefs is a reference to a list of monitoring Elasticsearch clusters running in the same Kubernetes cluster. Due to existing limitations, only a single Elasticsearch cluster is currently supported.",
                                                                    "items": {
                                                                        "description": "ObjectSelector defines a reference to a Kubernetes object which can be an Elastic resource managed by the operator or a Secret describing an external Elastic resource not managed by the operator.",
                                                                        "properties": {
                                                                            "name": {
                                                                                "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                                                "type": "string",
                                                                            },
                                                                            "namespace": {
                                                                                "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                                                "type": "string",
                                                                            },
                                                                            "secretName": {
                                                                                "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                                                "type": "string",
                                                                            },
                                                                            "serviceName": {
                                                                                "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                                                "type": "string",
                                                                            },
                                                                        },
                                                                        "type": "object",
                                                                    },
                                                                    "type": "array",
                                                                }
                                                            },
                                                            "type": "object",
                                                        },
                                                        "metrics": {
                                                            "description": "Metrics holds references to Elasticsearch clusters which receive monitoring data from this resource.",
                                                            "properties": {
                                                                "elasticsearchRefs": {
                                                                    "description": "ElasticsearchRefs is a reference to a list of monitoring Elasticsearch clusters running in the same Kubernetes cluster. Due to existing limitations, only a single Elasticsearch cluster is currently supported.",
                                                                    "items": {
                                                                        "description": "ObjectSelector defines a reference to a Kubernetes object which can be an Elastic resource managed by the operator or a Secret describing an external Elastic resource not managed by the operator.",
                                                                        "properties": {
                                                                            "name": {
                                                                                "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                                                "type": "string",
                                                                            },
                                                                            "namespace": {
                                                                                "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                                                "type": "string",
                                                                            },
                                                                            "secretName": {
                                                                                "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                                                "type": "string",
                                                                            },
                                                                            "serviceName": {
                                                                                "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                                                "type": "string",
                                                                            },
                                                                        },
                                                                        "type": "object",
                                                                    },
                                                                    "type": "array",
                                                                }
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "revisionHistoryLimit": {
                                                    "description": "RevisionHistoryLimit is the number of revisions to retain to allow rollback in the underlying DaemonSet or Deployment.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "secureSettings": {
                                                    "description": "SecureSettings is a list of references to Kubernetes Secrets containing sensitive configuration options for the Beat. Secrets data can be then referenced in the Beat config using the Secret's keys or as specified in `Entries` field of each SecureSetting.",
                                                    "items": {
                                                        "description": "SecretSource defines a data source based on a Kubernetes Secret.",
                                                        "properties": {
                                                            "entries": {
                                                                "description": "Entries define how to project each key-value pair in the secret to filesystem paths. If not defined, all keys will be projected to similarly named paths in the filesystem. If defined, only the specified keys will be projected to the corresponding paths.",
                                                                "items": {
                                                                    "description": "KeyToPath defines how to map a key in a Secret object to a filesystem path.",
                                                                    "properties": {
                                                                        "key": {
                                                                            "description": "Key is the key contained in the secret.",
                                                                            "type": "string",
                                                                        },
                                                                        "path": {
                                                                            "description": 'Path is the relative file path to map the key to. Path must not be an absolute file path and must not contain any ".." components.',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "required": ["key"],
                                                                    "type": "object",
                                                                },
                                                                "type": "array",
                                                            },
                                                            "secretName": {
                                                                "description": "SecretName is the name of the secret.",
                                                                "type": "string",
                                                            },
                                                        },
                                                        "required": ["secretName"],
                                                        "type": "object",
                                                    },
                                                    "type": "array",
                                                },
                                                "serviceAccountName": {
                                                    "description": "ServiceAccountName is used to check access from the current resource to Elasticsearch resource in a different namespace. Can only be used if ECK is enforcing RBAC on references.",
                                                    "type": "string",
                                                },
                                                "type": {
                                                    "description": "Type is the type of the Beat to deploy (filebeat, metricbeat, heartbeat, auditbeat, journalbeat, packetbeat, and so on). Any string can be used, but well-known types will have the image field defaulted and have the appropriate Elasticsearch roles created automatically. It also allows for dashboard setup when combined with a `KibanaRef`.",
                                                    "maxLength": 20,
                                                    "pattern": "[a-zA-Z0-9-]+",
                                                    "type": "string",
                                                },
                                                "version": {
                                                    "description": "Version of the Beat.",
                                                    "type": "string",
                                                },
                                            },
                                            "required": ["type", "version"],
                                            "type": "object",
                                        },
                                        "status": {
                                            "description": "BeatStatus defines the observed state of a Beat.",
                                            "properties": {
                                                "availableNodes": {
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "elasticsearchAssociationStatus": {
                                                    "description": "AssociationStatus is the status of an association resource.",
                                                    "type": "string",
                                                },
                                                "expectedNodes": {
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "health": {"type": "string"},
                                                "kibanaAssociationStatus": {
                                                    "description": "AssociationStatus is the status of an association resource.",
                                                    "type": "string",
                                                },
                                                "monitoringAssociationStatus": {
                                                    "additionalProperties": {
                                                        "description": "AssociationStatus is the status of an association resource.",
                                                        "type": "string",
                                                    },
                                                    "description": "AssociationStatusMap is the map of association's namespaced name string to its AssociationStatus. For resources that have a single Association of a given type (for ex. single ES reference), this map contains a single entry.",
                                                    "type": "object",
                                                },
                                                "observedGeneration": {
                                                    "description": "ObservedGeneration represents the .metadata.generation that the status is based upon. It corresponds to the metadata generation, which is updated on mutation by the API Server. If the generation observed in status diverges from the generation in metadata, the Beats controller has not yet processed the changes contained in the Beats specification.",
                                                    "format": "int64",
                                                    "type": "integer",
                                                },
                                                "version": {
                                                    "description": "Version of the stack resource currently running. During version upgrades, multiple versions may run in parallel: this value specifies the lowest version currently running.",
                                                    "type": "string",
                                                },
                                            },
                                            "type": "object",
                                        },
                                    },
                                    "type": "object",
                                }
                            },
                            "served": True,
                            "storage": True,
                            "subresources": {"status": {}},
                        }
                    ],
                },
            },
            {
                "apiVersion": "apiextensions.k8s.io/v1",
                "kind": "CustomResourceDefinition",
                "metadata": {
                    "annotations": {"controller-gen.kubebuilder.io/version": "v0.10.0"},
                    "creationTimestamp": None,
                    "labels": {
                        "app.kubernetes.io/instance": "elastic-operator",
                        "app.kubernetes.io/name": "eck-operator-crds",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                    "name": "elasticmapsservers.maps.k8s.elastic.co",
                },
                "spec": {
                    "group": "maps.k8s.elastic.co",
                    "names": {
                        "categories": ["elastic"],
                        "kind": "ElasticMapsServer",
                        "listKind": "ElasticMapsServerList",
                        "plural": "elasticmapsservers",
                        "shortNames": ["ems"],
                        "singular": "elasticmapsserver",
                    },
                    "scope": "Namespaced",
                    "versions": [
                        {
                            "additionalPrinterColumns": [
                                {
                                    "jsonPath": ".status.health",
                                    "name": "health",
                                    "type": "string",
                                },
                                {
                                    "description": "Available nodes",
                                    "jsonPath": ".status.availableNodes",
                                    "name": "nodes",
                                    "type": "integer",
                                },
                                {
                                    "description": "ElasticMapsServer version",
                                    "jsonPath": ".status.version",
                                    "name": "version",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".metadata.creationTimestamp",
                                    "name": "age",
                                    "type": "date",
                                },
                            ],
                            "name": "v1alpha1",
                            "schema": {
                                "openAPIV3Schema": {
                                    "description": "ElasticMapsServer represents an Elastic Map Server resource in a Kubernetes cluster.",
                                    "properties": {
                                        "apiVersion": {
                                            "description": "APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources",
                                            "type": "string",
                                        },
                                        "kind": {
                                            "description": "Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds",
                                            "type": "string",
                                        },
                                        "metadata": {"type": "object"},
                                        "spec": {
                                            "description": "MapsSpec holds the specification of an Elastic Maps Server instance.",
                                            "properties": {
                                                "config": {
                                                    "description": "Config holds the ElasticMapsServer configuration. See: https://www.elastic.co/guide/en/kibana/current/maps-connect-to-ems.html#elastic-maps-server-configuration",
                                                    "type": "object",
                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                },
                                                "configRef": {
                                                    "description": "ConfigRef contains a reference to an existing Kubernetes Secret holding the Elastic Maps Server configuration. Configuration settings are merged and have precedence over settings specified in `config`.",
                                                    "properties": {
                                                        "secretName": {
                                                            "description": "SecretName is the name of the secret.",
                                                            "type": "string",
                                                        }
                                                    },
                                                    "type": "object",
                                                },
                                                "count": {
                                                    "description": "Count of Elastic Maps Server instances to deploy.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "elasticsearchRef": {
                                                    "description": "ElasticsearchRef is a reference to an Elasticsearch cluster running in the same Kubernetes cluster.",
                                                    "properties": {
                                                        "name": {
                                                            "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                            "type": "string",
                                                        },
                                                        "namespace": {
                                                            "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                            "type": "string",
                                                        },
                                                        "secretName": {
                                                            "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                            "type": "string",
                                                        },
                                                        "serviceName": {
                                                            "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                            "type": "string",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "http": {
                                                    "description": "HTTP holds the HTTP layer configuration for Elastic Maps Server.",
                                                    "properties": {
                                                        "service": {
                                                            "description": "Service defines the template for the associated Kubernetes Service object.",
                                                            "properties": {
                                                                "metadata": {
                                                                    "description": "ObjectMeta is the metadata of the service. The name and namespace provided here are managed by ECK and will be ignored.",
                                                                    "properties": {
                                                                        "annotations": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "finalizers": {
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "labels": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "name": {
                                                                            "type": "string"
                                                                        },
                                                                        "namespace": {
                                                                            "type": "string"
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "spec": {
                                                                    "description": "Spec is the specification of the service.",
                                                                    "properties": {
                                                                        "allocateLoadBalancerNodePorts": {
                                                                            "description": 'allocateLoadBalancerNodePorts defines if NodePorts will be automatically allocated for services with type LoadBalancer.  Default is "true". It may be set to "false" if the cluster load-balancer does not rely on NodePorts.  If the caller requests specific NodePorts (by specifying a value), those requests will be respected, regardless of this field. This field may only be set for services with type LoadBalancer and will be cleared if the type is changed to any other type.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "clusterIP": {
                                                                            "description": 'clusterIP is the IP address of the service and is usually assigned randomly. If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be blank) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address. Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "clusterIPs": {
                                                                            "description": 'ClusterIPs is a list of IP addresses assigned to this service, and are usually assigned randomly.  If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be empty) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address.  Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName.  If this field is not specified, it will be initialized from the clusterIP field.  If this field is specified, clients must ensure that clusterIPs[0] and clusterIP have the same value. \n This field may hold a maximum of two entries (dual-stack IPs, in either order). These IPs must correspond to the values of the ipFamilies field. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "externalIPs": {
                                                                            "description": "externalIPs is a list of IP addresses for which nodes in the cluster will also accept traffic for this service.  These IPs are not managed by Kubernetes.  The user is responsible for ensuring that traffic arrives at a node with this IP.  A common example is external load-balancers that are not part of the Kubernetes system.",
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "externalName": {
                                                                            "description": 'externalName is the external reference that discovery mechanisms will return as an alias for this service (e.g. a DNS CNAME record). No proxying will be involved.  Must be a lowercase RFC-1123 hostname (https://tools.ietf.org/html/rfc1123) and requires `type` to be "ExternalName".',
                                                                            "type": "string",
                                                                        },
                                                                        "externalTrafficPolicy": {
                                                                            "description": 'externalTrafficPolicy describes how nodes distribute service traffic they receive on one of the Service\'s "externally-facing" addresses (NodePorts, ExternalIPs, and LoadBalancer IPs). If set to "Local", the proxy will configure the service in a way that assumes that external load balancers will take care of balancing the service traffic between nodes, and so each node will deliver traffic only to the node-local endpoints of the service, without masquerading the client source IP. (Traffic mistakenly sent to a node with no endpoints will be dropped.) The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features). Note that traffic sent to an External IP or LoadBalancer IP from within the cluster will always get "Cluster" semantics, but clients sending to a NodePort from within the cluster may need to take traffic policy into account when picking a node.',
                                                                            "type": "string",
                                                                        },
                                                                        "healthCheckNodePort": {
                                                                            "description": "healthCheckNodePort specifies the healthcheck nodePort for the service. This only applies when type is set to LoadBalancer and externalTrafficPolicy is set to Local. If a value is specified, is in-range, and is not in use, it will be used.  If not specified, a value will be automatically allocated.  External systems (e.g. load-balancers) can use this port to determine if a given node holds endpoints for this service or not.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type). This field cannot be updated once set.",
                                                                            "format": "int32",
                                                                            "type": "integer",
                                                                        },
                                                                        "internalTrafficPolicy": {
                                                                            "description": 'InternalTrafficPolicy describes how nodes distribute service traffic they receive on the ClusterIP. If set to "Local", the proxy will assume that pods only want to talk to endpoints of the service on the same node as the pod, dropping the traffic if there are no local endpoints. The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features).',
                                                                            "type": "string",
                                                                        },
                                                                        "ipFamilies": {
                                                                            "description": 'IPFamilies is a list of IP families (e.g. IPv4, IPv6) assigned to this service. This field is usually assigned automatically based on cluster configuration and the ipFamilyPolicy field. If this field is specified manually, the requested family is available in the cluster, and ipFamilyPolicy allows it, it will be used; otherwise creation of the service will fail. This field is conditionally mutable: it allows for adding or removing a secondary IP family, but it does not allow changing the primary IP family of the Service. Valid values are "IPv4" and "IPv6".  This field only applies to Services of types ClusterIP, NodePort, and LoadBalancer, and does apply to "headless" services. This field will be wiped when updating a Service to type ExternalName. \n This field may hold a maximum of two entries (dual-stack families, in either order).  These families must correspond to the values of the clusterIPs field, if specified. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field.',
                                                                            "items": {
                                                                                "description": "IPFamily represents the IP Family (IPv4 or IPv6). This type is used to express the family of an IP expressed by a type (e.g. service.spec.ipFamilies).",
                                                                                "type": "string",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "ipFamilyPolicy": {
                                                                            "description": 'IPFamilyPolicy represents the dual-stack-ness requested or required by this Service. If there is no value provided, then this field will be set to SingleStack. Services can be "SingleStack" (a single IP family), "PreferDualStack" (two IP families on dual-stack configured clusters or a single IP family on single-stack clusters), or "RequireDualStack" (two IP families on dual-stack configured clusters, otherwise fail). The ipFamilies and clusterIPs fields depend on the value of this field. This field will be wiped when updating a service to type ExternalName.',
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerClass": {
                                                                            "description": "loadBalancerClass is the class of the load balancer implementation this Service belongs to. If specified, the value of this field must be a label-style identifier, with an optional prefix, e.g. \"internal-vip\" or \"example.com/internal-vip\". Unprefixed names are reserved for end-users. This field can only be set when the Service type is 'LoadBalancer'. If not set, the default load balancer implementation is used, today this is typically done through the cloud provider integration, but should apply for any default implementation. If set, it is assumed that a load balancer implementation is watching for Services with a matching class. Any default load balancer implementation (e.g. cloud providers) should ignore Services that set this field. This field can only be set when creating or updating a Service to type 'LoadBalancer'. Once set, it can not be changed. This field will be wiped when a service is updated to a non 'LoadBalancer' type.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerIP": {
                                                                            "description": "Only applies to Service Type: LoadBalancer. This feature depends on whether the underlying cloud-provider supports specifying the loadBalancerIP when a load balancer is created. This field will be ignored if the cloud-provider does not support the feature. Deprecated: This field was under-specified and its meaning varies across implementations, and it cannot support dual-stack. As of Kubernetes v1.24, users are encouraged to use implementation-specific annotations when available. This field may be removed in a future API version.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerSourceRanges": {
                                                                            "description": 'If specified and supported by the platform, this will restrict traffic through the cloud-provider load-balancer will be restricted to the specified client IPs. This field will be ignored if the cloud-provider does not support the feature." More info: https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "ports": {
                                                                            "description": "The list of ports that are exposed by this service. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies",
                                                                            "items": {
                                                                                "description": "ServicePort contains information on service's port.",
                                                                                "properties": {
                                                                                    "appProtocol": {
                                                                                        "description": "The application protocol for this port. This field follows standard Kubernetes label syntax. Un-prefixed names are reserved for IANA standard service names (as per RFC-6335 and https://www.iana.org/assignments/service-names). Non-standard protocols should use prefixed names such as mycompany.com/my-custom-protocol.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "name": {
                                                                                        "description": "The name of this port within the service. This must be a DNS_LABEL. All ports within a ServiceSpec must have unique names. When considering the endpoints for a Service, this must match the 'name' field in the EndpointPort. Optional if only one ServicePort is defined on this service.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "nodePort": {
                                                                                        "description": "The port on each node on which this service is exposed when type is NodePort or LoadBalancer.  Usually assigned by the system. If a value is specified, in-range, and not in use it will be used, otherwise the operation will fail.  If not specified, a port will be allocated if this Service requires one.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type from NodePort to ClusterIP). More info: https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "port": {
                                                                                        "description": "The port that will be exposed by this service.",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "protocol": {
                                                                                        "default": "TCP",
                                                                                        "description": 'The IP protocol for this port. Supports "TCP", "UDP", and "SCTP". Default is TCP.',
                                                                                        "type": "string",
                                                                                    },
                                                                                    "targetPort": {
                                                                                        "anyOf": [
                                                                                            {
                                                                                                "type": "integer"
                                                                                            },
                                                                                            {
                                                                                                "type": "string"
                                                                                            },
                                                                                        ],
                                                                                        "description": "Number or name of the port to access on the pods targeted by the service. Number must be in the range 1 to 65535. Name must be an IANA_SVC_NAME. If this is a string, it will be looked up as a named port in the target Pod's container ports. If this is not specified, the value of the 'port' field is used (an identity map). This field is ignored for services with clusterIP=None, and should be omitted or set equal to the 'port' field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#defining-a-service",
                                                                                        "x-kubernetes-int-or-string": True,
                                                                                    },
                                                                                },
                                                                                "required": [
                                                                                    "port"
                                                                                ],
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-map-keys": [
                                                                                "port",
                                                                                "protocol",
                                                                            ],
                                                                            "x-kubernetes-list-type": "map",
                                                                        },
                                                                        "publishNotReadyAddresses": {
                                                                            "description": 'publishNotReadyAddresses indicates that any agent which deals with endpoints for this Service should disregard any indications of ready/not-ready. The primary use case for setting this field is for a StatefulSet\'s Headless Service to propagate SRV DNS records for its Pods for the purpose of peer discovery. The Kubernetes controllers that generate Endpoints and EndpointSlice resources for Services interpret this to mean that all endpoints are considered "ready" even if the Pods themselves are not. Agents which consume only Kubernetes generated endpoints through the Endpoints or EndpointSlice resources can safely assume this behavior.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "selector": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "description": "Route service traffic to pods with label keys and values matching this selector. If empty or not present, the service is assumed to have an external process managing its endpoints, which Kubernetes will not modify. Only applies to types ClusterIP, NodePort, and LoadBalancer. Ignored if type is ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/",
                                                                            "type": "object",
                                                                            "x-kubernetes-map-type": "atomic",
                                                                        },
                                                                        "sessionAffinity": {
                                                                            "description": 'Supports "ClientIP" and "None". Used to maintain session affinity. Enable client IP based session affinity. Must be ClientIP or None. Defaults to None. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "sessionAffinityConfig": {
                                                                            "description": "sessionAffinityConfig contains the configurations of session affinity.",
                                                                            "properties": {
                                                                                "clientIP": {
                                                                                    "description": "clientIP contains the configurations of Client IP based session affinity.",
                                                                                    "properties": {
                                                                                        "timeoutSeconds": {
                                                                                            "description": 'timeoutSeconds specifies the seconds of ClientIP type session sticky time. The value must be >0 && <=86400(for 1 day) if ServiceAffinity == "ClientIP". Default value is 10800(for 3 hours).',
                                                                                            "format": "int32",
                                                                                            "type": "integer",
                                                                                        }
                                                                                    },
                                                                                    "type": "object",
                                                                                }
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "type": {
                                                                            "description": 'type determines how the Service is exposed. Defaults to ClusterIP. Valid options are ExternalName, ClusterIP, NodePort, and LoadBalancer. "ClusterIP" allocates a cluster-internal IP address for load-balancing to endpoints. Endpoints are determined by the selector or if that is not specified, by manual construction of an Endpoints object or EndpointSlice objects. If clusterIP is "None", no virtual IP is allocated and the endpoints are published as a set of endpoints rather than a virtual IP. "NodePort" builds on ClusterIP and allocates a port on every node which routes to the same endpoints as the clusterIP. "LoadBalancer" builds on NodePort and creates an external load-balancer (if supported in the current cloud) which routes to the same endpoints as the clusterIP. "ExternalName" aliases this service to the specified externalName. Several other fields do not apply to ExternalName services. More info: https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                        "tls": {
                                                            "description": "TLS defines options for configuring TLS for HTTP.",
                                                            "properties": {
                                                                "certificate": {
                                                                    "description": "Certificate is a reference to a Kubernetes secret that contains the certificate and private key for enabling TLS. The referenced secret should contain the following: \n - `ca.crt`: The certificate authority (optional). - `tls.crt`: The certificate (or a chain). - `tls.key`: The private key to the first certificate in the certificate chain.",
                                                                    "properties": {
                                                                        "secretName": {
                                                                            "description": "SecretName is the name of the secret.",
                                                                            "type": "string",
                                                                        }
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "selfSignedCertificate": {
                                                                    "description": "SelfSignedCertificate allows configuring the self-signed certificate generated by the operator.",
                                                                    "properties": {
                                                                        "disabled": {
                                                                            "description": "Disabled indicates that the provisioning of the self-signed certifcate should be disabled.",
                                                                            "type": "boolean",
                                                                        },
                                                                        "subjectAltNames": {
                                                                            "description": "SubjectAlternativeNames is a list of SANs to include in the generated HTTP TLS certificate.",
                                                                            "items": {
                                                                                "description": "SubjectAlternativeName represents a SAN entry in a x509 certificate.",
                                                                                "properties": {
                                                                                    "dns": {
                                                                                        "description": "DNS is the DNS name of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "ip": {
                                                                                        "description": "IP is the IP address of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                },
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "image": {
                                                    "description": "Image is the Elastic Maps Server Docker image to deploy.",
                                                    "type": "string",
                                                },
                                                "podTemplate": {
                                                    "description": "PodTemplate provides customisation options (labels, annotations, affinity rules, resource requests, and so on) for the Elastic Maps Server pods",
                                                    "type": "object",
                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                },
                                                "revisionHistoryLimit": {
                                                    "description": "RevisionHistoryLimit is the number of revisions to retain to allow rollback in the underlying Deployment.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "serviceAccountName": {
                                                    "description": "ServiceAccountName is used to check access from the current resource to a resource (for ex. Elasticsearch) in a different namespace. Can only be used if ECK is enforcing RBAC on references.",
                                                    "type": "string",
                                                },
                                                "version": {
                                                    "description": "Version of Elastic Maps Server.",
                                                    "type": "string",
                                                },
                                            },
                                            "required": ["version"],
                                            "type": "object",
                                        },
                                        "status": {
                                            "description": "MapsStatus defines the observed state of Elastic Maps Server",
                                            "properties": {
                                                "associationStatus": {
                                                    "description": "AssociationStatus is the status of an association resource.",
                                                    "type": "string",
                                                },
                                                "availableNodes": {
                                                    "description": "AvailableNodes is the number of available replicas in the deployment.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "count": {
                                                    "description": "Count corresponds to Scale.Status.Replicas, which is the actual number of observed instances of the scaled object.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "health": {
                                                    "description": "Health of the deployment.",
                                                    "type": "string",
                                                },
                                                "observedGeneration": {
                                                    "description": "ObservedGeneration is the most recent generation observed for this Elastic Maps Server. It corresponds to the metadata generation, which is updated on mutation by the API Server. If the generation observed in status diverges from the generation in metadata, the Elastic Maps controller has not yet processed the changes contained in the Elastic Maps specification.",
                                                    "format": "int64",
                                                    "type": "integer",
                                                },
                                                "selector": {
                                                    "description": "Selector is the label selector used to find all pods.",
                                                    "type": "string",
                                                },
                                                "version": {
                                                    "description": "Version of the stack resource currently running. During version upgrades, multiple versions may run in parallel: this value specifies the lowest version currently running.",
                                                    "type": "string",
                                                },
                                            },
                                            "type": "object",
                                        },
                                    },
                                    "type": "object",
                                }
                            },
                            "served": True,
                            "storage": True,
                            "subresources": {
                                "scale": {
                                    "labelSelectorPath": ".status.selector",
                                    "specReplicasPath": ".spec.count",
                                    "statusReplicasPath": ".status.count",
                                },
                                "status": {},
                            },
                        }
                    ],
                },
            },
            {
                "apiVersion": "apiextensions.k8s.io/v1",
                "kind": "CustomResourceDefinition",
                "metadata": {
                    "annotations": {"controller-gen.kubebuilder.io/version": "v0.10.0"},
                    "creationTimestamp": None,
                    "labels": {
                        "app.kubernetes.io/instance": "elastic-operator",
                        "app.kubernetes.io/name": "eck-operator-crds",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                    "name": "elasticsearchautoscalers.autoscaling.k8s.elastic.co",
                },
                "spec": {
                    "group": "autoscaling.k8s.elastic.co",
                    "names": {
                        "categories": ["elastic"],
                        "kind": "ElasticsearchAutoscaler",
                        "listKind": "ElasticsearchAutoscalerList",
                        "plural": "elasticsearchautoscalers",
                        "shortNames": ["esa"],
                        "singular": "elasticsearchautoscaler",
                    },
                    "scope": "Namespaced",
                    "versions": [
                        {
                            "additionalPrinterColumns": [
                                {
                                    "jsonPath": ".spec.elasticsearchRef.name",
                                    "name": "Target",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".status.conditions[?(@.type=='Active')].status",
                                    "name": "Active",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".status.conditions[?(@.type=='Healthy')].status",
                                    "name": "Healthy",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".status.conditions[?(@.type=='Limited')].status",
                                    "name": "Limited",
                                    "type": "string",
                                },
                            ],
                            "name": "v1alpha1",
                            "schema": {
                                "openAPIV3Schema": {
                                    "description": "ElasticsearchAutoscaler represents an ElasticsearchAutoscaler resource in a Kubernetes cluster.",
                                    "properties": {
                                        "apiVersion": {
                                            "description": "APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources",
                                            "type": "string",
                                        },
                                        "kind": {
                                            "description": "Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds",
                                            "type": "string",
                                        },
                                        "metadata": {"type": "object"},
                                        "spec": {
                                            "description": "ElasticsearchAutoscalerSpec holds the specification of an Elasticsearch autoscaler resource.",
                                            "properties": {
                                                "elasticsearchRef": {
                                                    "description": "ElasticsearchRef is a reference to an Elasticsearch cluster that exists in the same namespace.",
                                                    "properties": {
                                                        "name": {
                                                            "description": "Name is the name of the Elasticsearch resource to scale automatically.",
                                                            "minLength": 1,
                                                            "type": "string",
                                                        }
                                                    },
                                                    "type": "object",
                                                },
                                                "policies": {
                                                    "items": {
                                                        "description": "AutoscalingPolicySpec holds a named autoscaling policy and the associated resources limits (cpu, memory, storage).",
                                                        "properties": {
                                                            "deciders": {
                                                                "additionalProperties": {
                                                                    "additionalProperties": {
                                                                        "type": "string"
                                                                    },
                                                                    "description": "DeciderSettings allow the user to tweak autoscaling deciders. The map data structure complies with the <key,value> format expected by Elasticsearch.",
                                                                    "type": "object",
                                                                },
                                                                "description": "Deciders allow the user to override default settings for autoscaling deciders.",
                                                                "type": "object",
                                                            },
                                                            "name": {
                                                                "description": "Name identifies the autoscaling policy in the autoscaling specification.",
                                                                "type": "string",
                                                            },
                                                            "resources": {
                                                                "description": "AutoscalingResources model the limits, submitted by the user, for the supported resources in an autoscaling policy. Only the node count range is mandatory. For other resources, a limit range is required only if the Elasticsearch autoscaling capacity API returns a requirement for a given resource. For example, the memory limit range is only required if the autoscaling API response contains a memory requirement. If there is no limit range for a resource, and if that resource is not mandatory, then the resources in the NodeSets managed by the autoscaling policy are left untouched.",
                                                                "properties": {
                                                                    "cpu": {
                                                                        "description": "QuantityRange models a resource limit range for resources which can be expressed with resource.Quantity.",
                                                                        "properties": {
                                                                            "max": {
                                                                                "anyOf": [
                                                                                    {
                                                                                        "type": "integer"
                                                                                    },
                                                                                    {
                                                                                        "type": "string"
                                                                                    },
                                                                                ],
                                                                                "description": "Max represents the upper limit for the resources managed by the autoscaler.",
                                                                                "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                                "x-kubernetes-int-or-string": True,
                                                                            },
                                                                            "min": {
                                                                                "anyOf": [
                                                                                    {
                                                                                        "type": "integer"
                                                                                    },
                                                                                    {
                                                                                        "type": "string"
                                                                                    },
                                                                                ],
                                                                                "description": "Min represents the lower limit for the resources managed by the autoscaler.",
                                                                                "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                                "x-kubernetes-int-or-string": True,
                                                                            },
                                                                            "requestsToLimitsRatio": {
                                                                                "anyOf": [
                                                                                    {
                                                                                        "type": "integer"
                                                                                    },
                                                                                    {
                                                                                        "type": "string"
                                                                                    },
                                                                                ],
                                                                                "description": "RequestsToLimitsRatio allows to customize Kubernetes resource Limit based on the Request.",
                                                                                "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                                "x-kubernetes-int-or-string": True,
                                                                            },
                                                                        },
                                                                        "required": [
                                                                            "max",
                                                                            "min",
                                                                        ],
                                                                        "type": "object",
                                                                    },
                                                                    "memory": {
                                                                        "description": "QuantityRange models a resource limit range for resources which can be expressed with resource.Quantity.",
                                                                        "properties": {
                                                                            "max": {
                                                                                "anyOf": [
                                                                                    {
                                                                                        "type": "integer"
                                                                                    },
                                                                                    {
                                                                                        "type": "string"
                                                                                    },
                                                                                ],
                                                                                "description": "Max represents the upper limit for the resources managed by the autoscaler.",
                                                                                "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                                "x-kubernetes-int-or-string": True,
                                                                            },
                                                                            "min": {
                                                                                "anyOf": [
                                                                                    {
                                                                                        "type": "integer"
                                                                                    },
                                                                                    {
                                                                                        "type": "string"
                                                                                    },
                                                                                ],
                                                                                "description": "Min represents the lower limit for the resources managed by the autoscaler.",
                                                                                "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                                "x-kubernetes-int-or-string": True,
                                                                            },
                                                                            "requestsToLimitsRatio": {
                                                                                "anyOf": [
                                                                                    {
                                                                                        "type": "integer"
                                                                                    },
                                                                                    {
                                                                                        "type": "string"
                                                                                    },
                                                                                ],
                                                                                "description": "RequestsToLimitsRatio allows to customize Kubernetes resource Limit based on the Request.",
                                                                                "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                                "x-kubernetes-int-or-string": True,
                                                                            },
                                                                        },
                                                                        "required": [
                                                                            "max",
                                                                            "min",
                                                                        ],
                                                                        "type": "object",
                                                                    },
                                                                    "nodeCount": {
                                                                        "description": "NodeCountRange is used to model the minimum and the maximum number of nodes over all the NodeSets managed by the same autoscaling policy.",
                                                                        "properties": {
                                                                            "max": {
                                                                                "description": "Max represents the maximum number of nodes in a tier.",
                                                                                "format": "int32",
                                                                                "type": "integer",
                                                                            },
                                                                            "min": {
                                                                                "description": "Min represents the minimum number of nodes in a tier.",
                                                                                "format": "int32",
                                                                                "type": "integer",
                                                                            },
                                                                        },
                                                                        "required": [
                                                                            "max",
                                                                            "min",
                                                                        ],
                                                                        "type": "object",
                                                                    },
                                                                    "storage": {
                                                                        "description": "QuantityRange models a resource limit range for resources which can be expressed with resource.Quantity.",
                                                                        "properties": {
                                                                            "max": {
                                                                                "anyOf": [
                                                                                    {
                                                                                        "type": "integer"
                                                                                    },
                                                                                    {
                                                                                        "type": "string"
                                                                                    },
                                                                                ],
                                                                                "description": "Max represents the upper limit for the resources managed by the autoscaler.",
                                                                                "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                                "x-kubernetes-int-or-string": True,
                                                                            },
                                                                            "min": {
                                                                                "anyOf": [
                                                                                    {
                                                                                        "type": "integer"
                                                                                    },
                                                                                    {
                                                                                        "type": "string"
                                                                                    },
                                                                                ],
                                                                                "description": "Min represents the lower limit for the resources managed by the autoscaler.",
                                                                                "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                                "x-kubernetes-int-or-string": True,
                                                                            },
                                                                            "requestsToLimitsRatio": {
                                                                                "anyOf": [
                                                                                    {
                                                                                        "type": "integer"
                                                                                    },
                                                                                    {
                                                                                        "type": "string"
                                                                                    },
                                                                                ],
                                                                                "description": "RequestsToLimitsRatio allows to customize Kubernetes resource Limit based on the Request.",
                                                                                "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                                "x-kubernetes-int-or-string": True,
                                                                            },
                                                                        },
                                                                        "required": [
                                                                            "max",
                                                                            "min",
                                                                        ],
                                                                        "type": "object",
                                                                    },
                                                                },
                                                                "required": [
                                                                    "nodeCount"
                                                                ],
                                                                "type": "object",
                                                            },
                                                            "roles": {
                                                                "description": "An autoscaling policy must target a unique set of roles.",
                                                                "items": {
                                                                    "type": "string"
                                                                },
                                                                "type": "array",
                                                            },
                                                        },
                                                        "required": ["resources"],
                                                        "type": "object",
                                                    },
                                                    "type": "array",
                                                },
                                                "pollingPeriod": {
                                                    "description": "PollingPeriod is the period at which to synchronize with the Elasticsearch autoscaling API.",
                                                    "type": "string",
                                                },
                                            },
                                            "required": ["policies"],
                                            "type": "object",
                                        },
                                        "status": {
                                            "properties": {
                                                "conditions": {
                                                    "description": "Conditions holds the current service state of the autoscaling controller.",
                                                    "items": {
                                                        "description": "Condition represents Elasticsearch resource's condition. **This API is in technical preview and may be changed or removed in a future release.**",
                                                        "properties": {
                                                            "lastTransitionTime": {
                                                                "format": "date-time",
                                                                "type": "string",
                                                            },
                                                            "message": {
                                                                "type": "string"
                                                            },
                                                            "status": {
                                                                "type": "string"
                                                            },
                                                            "type": {
                                                                "description": "ConditionType defines the condition of an Elasticsearch resource.",
                                                                "type": "string",
                                                            },
                                                        },
                                                        "required": ["status", "type"],
                                                        "type": "object",
                                                    },
                                                    "type": "array",
                                                },
                                                "observedGeneration": {
                                                    "description": "ObservedGeneration is the last observed generation by the controller.",
                                                    "format": "int64",
                                                    "type": "integer",
                                                },
                                                "policies": {
                                                    "description": "AutoscalingPolicyStatuses is used to expose state messages to user or external system.",
                                                    "items": {
                                                        "properties": {
                                                            "lastModificationTime": {
                                                                "description": "LastModificationTime is the last time the resources have been updated, used by the cooldown algorithm.",
                                                                "format": "date-time",
                                                                "type": "string",
                                                            },
                                                            "name": {
                                                                "description": "Name is the name of the autoscaling policy",
                                                                "type": "string",
                                                            },
                                                            "nodeSets": {
                                                                "description": "NodeSetNodeCount holds the number of nodes for each nodeSet.",
                                                                "items": {
                                                                    "description": "NodeSetNodeCount models the number of nodes expected in a given NodeSet.",
                                                                    "properties": {
                                                                        "name": {
                                                                            "description": "Name of the Nodeset.",
                                                                            "type": "string",
                                                                        },
                                                                        "nodeCount": {
                                                                            "description": "NodeCount is the number of nodes, as computed by the autoscaler, expected in this NodeSet.",
                                                                            "format": "int32",
                                                                            "type": "integer",
                                                                        },
                                                                    },
                                                                    "required": [
                                                                        "name",
                                                                        "nodeCount",
                                                                    ],
                                                                    "type": "object",
                                                                },
                                                                "type": "array",
                                                            },
                                                            "resources": {
                                                                "description": "ResourcesSpecification holds the resource values common to all the nodeSets managed by a same autoscaling policy. Only the resources managed by the autoscaling controller are saved in the Status.",
                                                                "properties": {
                                                                    "limits": {
                                                                        "additionalProperties": {
                                                                            "anyOf": [
                                                                                {
                                                                                    "type": "integer"
                                                                                },
                                                                                {
                                                                                    "type": "string"
                                                                                },
                                                                            ],
                                                                            "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                            "x-kubernetes-int-or-string": True,
                                                                        },
                                                                        "description": "ResourceList is a set of (resource name, quantity) pairs.",
                                                                        "type": "object",
                                                                    },
                                                                    "requests": {
                                                                        "additionalProperties": {
                                                                            "anyOf": [
                                                                                {
                                                                                    "type": "integer"
                                                                                },
                                                                                {
                                                                                    "type": "string"
                                                                                },
                                                                            ],
                                                                            "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                            "x-kubernetes-int-or-string": True,
                                                                        },
                                                                        "description": "ResourceList is a set of (resource name, quantity) pairs.",
                                                                        "type": "object",
                                                                    },
                                                                },
                                                                "type": "object",
                                                            },
                                                            "state": {
                                                                "description": "PolicyStates may contain various messages regarding the current state of this autoscaling policy.",
                                                                "items": {
                                                                    "properties": {
                                                                        "messages": {
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "type": {
                                                                            "type": "string"
                                                                        },
                                                                    },
                                                                    "required": [
                                                                        "messages",
                                                                        "type",
                                                                    ],
                                                                    "type": "object",
                                                                },
                                                                "type": "array",
                                                            },
                                                        },
                                                        "required": ["name"],
                                                        "type": "object",
                                                    },
                                                    "type": "array",
                                                },
                                            },
                                            "type": "object",
                                        },
                                    },
                                    "type": "object",
                                }
                            },
                            "served": True,
                            "storage": True,
                            "subresources": {"status": {}},
                        }
                    ],
                },
            },
            {
                "apiVersion": "apiextensions.k8s.io/v1",
                "kind": "CustomResourceDefinition",
                "metadata": {
                    "annotations": {"controller-gen.kubebuilder.io/version": "v0.10.0"},
                    "creationTimestamp": None,
                    "labels": {
                        "app.kubernetes.io/instance": "elastic-operator",
                        "app.kubernetes.io/name": "eck-operator-crds",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                    "name": "elasticsearches.elasticsearch.k8s.elastic.co",
                },
                "spec": {
                    "group": "elasticsearch.k8s.elastic.co",
                    "names": {
                        "categories": ["elastic"],
                        "kind": "Elasticsearch",
                        "listKind": "ElasticsearchList",
                        "plural": "elasticsearches",
                        "shortNames": ["es"],
                        "singular": "elasticsearch",
                    },
                    "scope": "Namespaced",
                    "versions": [
                        {
                            "additionalPrinterColumns": [
                                {
                                    "jsonPath": ".status.health",
                                    "name": "health",
                                    "type": "string",
                                },
                                {
                                    "description": "Available nodes",
                                    "jsonPath": ".status.availableNodes",
                                    "name": "nodes",
                                    "type": "integer",
                                },
                                {
                                    "description": "Elasticsearch version",
                                    "jsonPath": ".status.version",
                                    "name": "version",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".status.phase",
                                    "name": "phase",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".metadata.creationTimestamp",
                                    "name": "age",
                                    "type": "date",
                                },
                            ],
                            "name": "v1",
                            "schema": {
                                "openAPIV3Schema": {
                                    "description": "Elasticsearch represents an Elasticsearch resource in a Kubernetes cluster.",
                                    "properties": {
                                        "apiVersion": {
                                            "description": "APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources",
                                            "type": "string",
                                        },
                                        "kind": {
                                            "description": "Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds",
                                            "type": "string",
                                        },
                                        "metadata": {"type": "object"},
                                        "spec": {
                                            "description": "ElasticsearchSpec holds the specification of an Elasticsearch cluster.",
                                            "properties": {
                                                "auth": {
                                                    "description": "Auth contains user authentication and authorization security settings for Elasticsearch.",
                                                    "properties": {
                                                        "fileRealm": {
                                                            "description": "FileRealm to propagate to the Elasticsearch cluster.",
                                                            "items": {
                                                                "description": "FileRealmSource references users to create in the Elasticsearch cluster.",
                                                                "properties": {
                                                                    "secretName": {
                                                                        "description": "SecretName is the name of the secret.",
                                                                        "type": "string",
                                                                    }
                                                                },
                                                                "type": "object",
                                                            },
                                                            "type": "array",
                                                        },
                                                        "roles": {
                                                            "description": "Roles to propagate to the Elasticsearch cluster.",
                                                            "items": {
                                                                "description": "RoleSource references roles to create in the Elasticsearch cluster.",
                                                                "properties": {
                                                                    "secretName": {
                                                                        "description": "SecretName is the name of the secret.",
                                                                        "type": "string",
                                                                    }
                                                                },
                                                                "type": "object",
                                                            },
                                                            "type": "array",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "http": {
                                                    "description": "HTTP holds HTTP layer settings for Elasticsearch.",
                                                    "properties": {
                                                        "service": {
                                                            "description": "Service defines the template for the associated Kubernetes Service object.",
                                                            "properties": {
                                                                "metadata": {
                                                                    "description": "ObjectMeta is the metadata of the service. The name and namespace provided here are managed by ECK and will be ignored.",
                                                                    "properties": {
                                                                        "annotations": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "finalizers": {
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "labels": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "name": {
                                                                            "type": "string"
                                                                        },
                                                                        "namespace": {
                                                                            "type": "string"
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "spec": {
                                                                    "description": "Spec is the specification of the service.",
                                                                    "properties": {
                                                                        "allocateLoadBalancerNodePorts": {
                                                                            "description": 'allocateLoadBalancerNodePorts defines if NodePorts will be automatically allocated for services with type LoadBalancer.  Default is "true". It may be set to "false" if the cluster load-balancer does not rely on NodePorts.  If the caller requests specific NodePorts (by specifying a value), those requests will be respected, regardless of this field. This field may only be set for services with type LoadBalancer and will be cleared if the type is changed to any other type.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "clusterIP": {
                                                                            "description": 'clusterIP is the IP address of the service and is usually assigned randomly. If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be blank) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address. Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "clusterIPs": {
                                                                            "description": 'ClusterIPs is a list of IP addresses assigned to this service, and are usually assigned randomly.  If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be empty) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address.  Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName.  If this field is not specified, it will be initialized from the clusterIP field.  If this field is specified, clients must ensure that clusterIPs[0] and clusterIP have the same value. \n This field may hold a maximum of two entries (dual-stack IPs, in either order). These IPs must correspond to the values of the ipFamilies field. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "externalIPs": {
                                                                            "description": "externalIPs is a list of IP addresses for which nodes in the cluster will also accept traffic for this service.  These IPs are not managed by Kubernetes.  The user is responsible for ensuring that traffic arrives at a node with this IP.  A common example is external load-balancers that are not part of the Kubernetes system.",
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "externalName": {
                                                                            "description": 'externalName is the external reference that discovery mechanisms will return as an alias for this service (e.g. a DNS CNAME record). No proxying will be involved.  Must be a lowercase RFC-1123 hostname (https://tools.ietf.org/html/rfc1123) and requires `type` to be "ExternalName".',
                                                                            "type": "string",
                                                                        },
                                                                        "externalTrafficPolicy": {
                                                                            "description": 'externalTrafficPolicy describes how nodes distribute service traffic they receive on one of the Service\'s "externally-facing" addresses (NodePorts, ExternalIPs, and LoadBalancer IPs). If set to "Local", the proxy will configure the service in a way that assumes that external load balancers will take care of balancing the service traffic between nodes, and so each node will deliver traffic only to the node-local endpoints of the service, without masquerading the client source IP. (Traffic mistakenly sent to a node with no endpoints will be dropped.) The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features). Note that traffic sent to an External IP or LoadBalancer IP from within the cluster will always get "Cluster" semantics, but clients sending to a NodePort from within the cluster may need to take traffic policy into account when picking a node.',
                                                                            "type": "string",
                                                                        },
                                                                        "healthCheckNodePort": {
                                                                            "description": "healthCheckNodePort specifies the healthcheck nodePort for the service. This only applies when type is set to LoadBalancer and externalTrafficPolicy is set to Local. If a value is specified, is in-range, and is not in use, it will be used.  If not specified, a value will be automatically allocated.  External systems (e.g. load-balancers) can use this port to determine if a given node holds endpoints for this service or not.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type). This field cannot be updated once set.",
                                                                            "format": "int32",
                                                                            "type": "integer",
                                                                        },
                                                                        "internalTrafficPolicy": {
                                                                            "description": 'InternalTrafficPolicy describes how nodes distribute service traffic they receive on the ClusterIP. If set to "Local", the proxy will assume that pods only want to talk to endpoints of the service on the same node as the pod, dropping the traffic if there are no local endpoints. The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features).',
                                                                            "type": "string",
                                                                        },
                                                                        "ipFamilies": {
                                                                            "description": 'IPFamilies is a list of IP families (e.g. IPv4, IPv6) assigned to this service. This field is usually assigned automatically based on cluster configuration and the ipFamilyPolicy field. If this field is specified manually, the requested family is available in the cluster, and ipFamilyPolicy allows it, it will be used; otherwise creation of the service will fail. This field is conditionally mutable: it allows for adding or removing a secondary IP family, but it does not allow changing the primary IP family of the Service. Valid values are "IPv4" and "IPv6".  This field only applies to Services of types ClusterIP, NodePort, and LoadBalancer, and does apply to "headless" services. This field will be wiped when updating a Service to type ExternalName. \n This field may hold a maximum of two entries (dual-stack families, in either order).  These families must correspond to the values of the clusterIPs field, if specified. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field.',
                                                                            "items": {
                                                                                "description": "IPFamily represents the IP Family (IPv4 or IPv6). This type is used to express the family of an IP expressed by a type (e.g. service.spec.ipFamilies).",
                                                                                "type": "string",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "ipFamilyPolicy": {
                                                                            "description": 'IPFamilyPolicy represents the dual-stack-ness requested or required by this Service. If there is no value provided, then this field will be set to SingleStack. Services can be "SingleStack" (a single IP family), "PreferDualStack" (two IP families on dual-stack configured clusters or a single IP family on single-stack clusters), or "RequireDualStack" (two IP families on dual-stack configured clusters, otherwise fail). The ipFamilies and clusterIPs fields depend on the value of this field. This field will be wiped when updating a service to type ExternalName.',
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerClass": {
                                                                            "description": "loadBalancerClass is the class of the load balancer implementation this Service belongs to. If specified, the value of this field must be a label-style identifier, with an optional prefix, e.g. \"internal-vip\" or \"example.com/internal-vip\". Unprefixed names are reserved for end-users. This field can only be set when the Service type is 'LoadBalancer'. If not set, the default load balancer implementation is used, today this is typically done through the cloud provider integration, but should apply for any default implementation. If set, it is assumed that a load balancer implementation is watching for Services with a matching class. Any default load balancer implementation (e.g. cloud providers) should ignore Services that set this field. This field can only be set when creating or updating a Service to type 'LoadBalancer'. Once set, it can not be changed. This field will be wiped when a service is updated to a non 'LoadBalancer' type.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerIP": {
                                                                            "description": "Only applies to Service Type: LoadBalancer. This feature depends on whether the underlying cloud-provider supports specifying the loadBalancerIP when a load balancer is created. This field will be ignored if the cloud-provider does not support the feature. Deprecated: This field was under-specified and its meaning varies across implementations, and it cannot support dual-stack. As of Kubernetes v1.24, users are encouraged to use implementation-specific annotations when available. This field may be removed in a future API version.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerSourceRanges": {
                                                                            "description": 'If specified and supported by the platform, this will restrict traffic through the cloud-provider load-balancer will be restricted to the specified client IPs. This field will be ignored if the cloud-provider does not support the feature." More info: https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "ports": {
                                                                            "description": "The list of ports that are exposed by this service. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies",
                                                                            "items": {
                                                                                "description": "ServicePort contains information on service's port.",
                                                                                "properties": {
                                                                                    "appProtocol": {
                                                                                        "description": "The application protocol for this port. This field follows standard Kubernetes label syntax. Un-prefixed names are reserved for IANA standard service names (as per RFC-6335 and https://www.iana.org/assignments/service-names). Non-standard protocols should use prefixed names such as mycompany.com/my-custom-protocol.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "name": {
                                                                                        "description": "The name of this port within the service. This must be a DNS_LABEL. All ports within a ServiceSpec must have unique names. When considering the endpoints for a Service, this must match the 'name' field in the EndpointPort. Optional if only one ServicePort is defined on this service.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "nodePort": {
                                                                                        "description": "The port on each node on which this service is exposed when type is NodePort or LoadBalancer.  Usually assigned by the system. If a value is specified, in-range, and not in use it will be used, otherwise the operation will fail.  If not specified, a port will be allocated if this Service requires one.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type from NodePort to ClusterIP). More info: https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "port": {
                                                                                        "description": "The port that will be exposed by this service.",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "protocol": {
                                                                                        "default": "TCP",
                                                                                        "description": 'The IP protocol for this port. Supports "TCP", "UDP", and "SCTP". Default is TCP.',
                                                                                        "type": "string",
                                                                                    },
                                                                                    "targetPort": {
                                                                                        "anyOf": [
                                                                                            {
                                                                                                "type": "integer"
                                                                                            },
                                                                                            {
                                                                                                "type": "string"
                                                                                            },
                                                                                        ],
                                                                                        "description": "Number or name of the port to access on the pods targeted by the service. Number must be in the range 1 to 65535. Name must be an IANA_SVC_NAME. If this is a string, it will be looked up as a named port in the target Pod's container ports. If this is not specified, the value of the 'port' field is used (an identity map). This field is ignored for services with clusterIP=None, and should be omitted or set equal to the 'port' field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#defining-a-service",
                                                                                        "x-kubernetes-int-or-string": True,
                                                                                    },
                                                                                },
                                                                                "required": [
                                                                                    "port"
                                                                                ],
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-map-keys": [
                                                                                "port",
                                                                                "protocol",
                                                                            ],
                                                                            "x-kubernetes-list-type": "map",
                                                                        },
                                                                        "publishNotReadyAddresses": {
                                                                            "description": 'publishNotReadyAddresses indicates that any agent which deals with endpoints for this Service should disregard any indications of ready/not-ready. The primary use case for setting this field is for a StatefulSet\'s Headless Service to propagate SRV DNS records for its Pods for the purpose of peer discovery. The Kubernetes controllers that generate Endpoints and EndpointSlice resources for Services interpret this to mean that all endpoints are considered "ready" even if the Pods themselves are not. Agents which consume only Kubernetes generated endpoints through the Endpoints or EndpointSlice resources can safely assume this behavior.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "selector": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "description": "Route service traffic to pods with label keys and values matching this selector. If empty or not present, the service is assumed to have an external process managing its endpoints, which Kubernetes will not modify. Only applies to types ClusterIP, NodePort, and LoadBalancer. Ignored if type is ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/",
                                                                            "type": "object",
                                                                            "x-kubernetes-map-type": "atomic",
                                                                        },
                                                                        "sessionAffinity": {
                                                                            "description": 'Supports "ClientIP" and "None". Used to maintain session affinity. Enable client IP based session affinity. Must be ClientIP or None. Defaults to None. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "sessionAffinityConfig": {
                                                                            "description": "sessionAffinityConfig contains the configurations of session affinity.",
                                                                            "properties": {
                                                                                "clientIP": {
                                                                                    "description": "clientIP contains the configurations of Client IP based session affinity.",
                                                                                    "properties": {
                                                                                        "timeoutSeconds": {
                                                                                            "description": 'timeoutSeconds specifies the seconds of ClientIP type session sticky time. The value must be >0 && <=86400(for 1 day) if ServiceAffinity == "ClientIP". Default value is 10800(for 3 hours).',
                                                                                            "format": "int32",
                                                                                            "type": "integer",
                                                                                        }
                                                                                    },
                                                                                    "type": "object",
                                                                                }
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "type": {
                                                                            "description": 'type determines how the Service is exposed. Defaults to ClusterIP. Valid options are ExternalName, ClusterIP, NodePort, and LoadBalancer. "ClusterIP" allocates a cluster-internal IP address for load-balancing to endpoints. Endpoints are determined by the selector or if that is not specified, by manual construction of an Endpoints object or EndpointSlice objects. If clusterIP is "None", no virtual IP is allocated and the endpoints are published as a set of endpoints rather than a virtual IP. "NodePort" builds on ClusterIP and allocates a port on every node which routes to the same endpoints as the clusterIP. "LoadBalancer" builds on NodePort and creates an external load-balancer (if supported in the current cloud) which routes to the same endpoints as the clusterIP. "ExternalName" aliases this service to the specified externalName. Several other fields do not apply to ExternalName services. More info: https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                        "tls": {
                                                            "description": "TLS defines options for configuring TLS for HTTP.",
                                                            "properties": {
                                                                "certificate": {
                                                                    "description": "Certificate is a reference to a Kubernetes secret that contains the certificate and private key for enabling TLS. The referenced secret should contain the following: \n - `ca.crt`: The certificate authority (optional). - `tls.crt`: The certificate (or a chain). - `tls.key`: The private key to the first certificate in the certificate chain.",
                                                                    "properties": {
                                                                        "secretName": {
                                                                            "description": "SecretName is the name of the secret.",
                                                                            "type": "string",
                                                                        }
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "selfSignedCertificate": {
                                                                    "description": "SelfSignedCertificate allows configuring the self-signed certificate generated by the operator.",
                                                                    "properties": {
                                                                        "disabled": {
                                                                            "description": "Disabled indicates that the provisioning of the self-signed certifcate should be disabled.",
                                                                            "type": "boolean",
                                                                        },
                                                                        "subjectAltNames": {
                                                                            "description": "SubjectAlternativeNames is a list of SANs to include in the generated HTTP TLS certificate.",
                                                                            "items": {
                                                                                "description": "SubjectAlternativeName represents a SAN entry in a x509 certificate.",
                                                                                "properties": {
                                                                                    "dns": {
                                                                                        "description": "DNS is the DNS name of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "ip": {
                                                                                        "description": "IP is the IP address of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                },
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "image": {
                                                    "description": "Image is the Elasticsearch Docker image to deploy.",
                                                    "type": "string",
                                                },
                                                "monitoring": {
                                                    "description": "Monitoring enables you to collect and ship log and monitoring data of this Elasticsearch cluster. See https://www.elastic.co/guide/en/elasticsearch/reference/current/monitor-elasticsearch-cluster.html. Metricbeat and Filebeat are deployed in the same Pod as sidecars and each one sends data to one or two different Elasticsearch monitoring clusters running in the same Kubernetes cluster.",
                                                    "properties": {
                                                        "logs": {
                                                            "description": "Logs holds references to Elasticsearch clusters which receive log data from an associated resource.",
                                                            "properties": {
                                                                "elasticsearchRefs": {
                                                                    "description": "ElasticsearchRefs is a reference to a list of monitoring Elasticsearch clusters running in the same Kubernetes cluster. Due to existing limitations, only a single Elasticsearch cluster is currently supported.",
                                                                    "items": {
                                                                        "description": "ObjectSelector defines a reference to a Kubernetes object which can be an Elastic resource managed by the operator or a Secret describing an external Elastic resource not managed by the operator.",
                                                                        "properties": {
                                                                            "name": {
                                                                                "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                                                "type": "string",
                                                                            },
                                                                            "namespace": {
                                                                                "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                                                "type": "string",
                                                                            },
                                                                            "secretName": {
                                                                                "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                                                "type": "string",
                                                                            },
                                                                            "serviceName": {
                                                                                "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                                                "type": "string",
                                                                            },
                                                                        },
                                                                        "type": "object",
                                                                    },
                                                                    "type": "array",
                                                                }
                                                            },
                                                            "type": "object",
                                                        },
                                                        "metrics": {
                                                            "description": "Metrics holds references to Elasticsearch clusters which receive monitoring data from this resource.",
                                                            "properties": {
                                                                "elasticsearchRefs": {
                                                                    "description": "ElasticsearchRefs is a reference to a list of monitoring Elasticsearch clusters running in the same Kubernetes cluster. Due to existing limitations, only a single Elasticsearch cluster is currently supported.",
                                                                    "items": {
                                                                        "description": "ObjectSelector defines a reference to a Kubernetes object which can be an Elastic resource managed by the operator or a Secret describing an external Elastic resource not managed by the operator.",
                                                                        "properties": {
                                                                            "name": {
                                                                                "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                                                "type": "string",
                                                                            },
                                                                            "namespace": {
                                                                                "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                                                "type": "string",
                                                                            },
                                                                            "secretName": {
                                                                                "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                                                "type": "string",
                                                                            },
                                                                            "serviceName": {
                                                                                "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                                                "type": "string",
                                                                            },
                                                                        },
                                                                        "type": "object",
                                                                    },
                                                                    "type": "array",
                                                                }
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "nodeSets": {
                                                    "description": "NodeSets allow specifying groups of Elasticsearch nodes sharing the same configuration and Pod templates.",
                                                    "items": {
                                                        "description": "NodeSet is the specification for a group of Elasticsearch nodes sharing the same configuration and a Pod template.",
                                                        "properties": {
                                                            "config": {
                                                                "description": "Config holds the Elasticsearch configuration.",
                                                                "type": "object",
                                                                "x-kubernetes-preserve-unknown-fields": True,
                                                            },
                                                            "count": {
                                                                "description": "Count of Elasticsearch nodes to deploy. If the node set is managed by an autoscaling policy the initial value is automatically set by the autoscaling controller.",
                                                                "format": "int32",
                                                                "type": "integer",
                                                            },
                                                            "name": {
                                                                "description": "Name of this set of nodes. Becomes a part of the Elasticsearch node.name setting.",
                                                                "maxLength": 23,
                                                                "pattern": "[a-zA-Z0-9-]+",
                                                                "type": "string",
                                                            },
                                                            "podTemplate": {
                                                                "description": "PodTemplate provides customisation options (labels, annotations, affinity rules, resource requests, and so on) for the Pods belonging to this NodeSet.",
                                                                "type": "object",
                                                                "x-kubernetes-preserve-unknown-fields": True,
                                                            },
                                                            "volumeClaimTemplates": {
                                                                "description": "VolumeClaimTemplates is a list of persistent volume claims to be used by each Pod in this NodeSet. Every claim in this list must have a matching volumeMount in one of the containers defined in the PodTemplate. Items defined here take precedence over any default claims added by the operator with the same name.",
                                                                "items": {
                                                                    "description": "PersistentVolumeClaim is a user's request for and claim to a persistent volume",
                                                                    "properties": {
                                                                        "apiVersion": {
                                                                            "description": "APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources",
                                                                            "type": "string",
                                                                        },
                                                                        "kind": {
                                                                            "description": "Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds",
                                                                            "type": "string",
                                                                        },
                                                                        "metadata": {
                                                                            "description": "Standard object's metadata. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#metadata",
                                                                            "properties": {
                                                                                "annotations": {
                                                                                    "additionalProperties": {
                                                                                        "type": "string"
                                                                                    },
                                                                                    "type": "object",
                                                                                },
                                                                                "finalizers": {
                                                                                    "items": {
                                                                                        "type": "string"
                                                                                    },
                                                                                    "type": "array",
                                                                                },
                                                                                "labels": {
                                                                                    "additionalProperties": {
                                                                                        "type": "string"
                                                                                    },
                                                                                    "type": "object",
                                                                                },
                                                                                "name": {
                                                                                    "type": "string"
                                                                                },
                                                                                "namespace": {
                                                                                    "type": "string"
                                                                                },
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "spec": {
                                                                            "description": "spec defines the desired characteristics of a volume requested by a pod author. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#persistentvolumeclaims",
                                                                            "properties": {
                                                                                "accessModes": {
                                                                                    "description": "accessModes contains the desired access modes the volume should have. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#access-modes-1",
                                                                                    "items": {
                                                                                        "type": "string"
                                                                                    },
                                                                                    "type": "array",
                                                                                },
                                                                                "dataSource": {
                                                                                    "description": "dataSource field can be used to specify either: * An existing VolumeSnapshot object (snapshot.storage.k8s.io/VolumeSnapshot) * An existing PVC (PersistentVolumeClaim) If the provisioner or an external controller can support the specified data source, it will create a new volume based on the contents of the specified data source. If the AnyVolumeDataSource feature gate is enabled, this field will always have the same contents as the DataSourceRef field.",
                                                                                    "properties": {
                                                                                        "apiGroup": {
                                                                                            "description": "APIGroup is the group for the resource being referenced. If APIGroup is not specified, the specified Kind must be in the core API group. For any other third-party types, APIGroup is required.",
                                                                                            "type": "string",
                                                                                        },
                                                                                        "kind": {
                                                                                            "description": "Kind is the type of resource being referenced",
                                                                                            "type": "string",
                                                                                        },
                                                                                        "name": {
                                                                                            "description": "Name is the name of resource being referenced",
                                                                                            "type": "string",
                                                                                        },
                                                                                    },
                                                                                    "required": [
                                                                                        "kind",
                                                                                        "name",
                                                                                    ],
                                                                                    "type": "object",
                                                                                    "x-kubernetes-map-type": "atomic",
                                                                                },
                                                                                "dataSourceRef": {
                                                                                    "description": "dataSourceRef specifies the object from which to populate the volume with data, if a non-empty volume is desired. This may be any local object from a non-empty API group (non core object) or a PersistentVolumeClaim object. When this field is specified, volume binding will only succeed if the type of the specified object matches some installed volume populator or dynamic provisioner. This field will replace the functionality of the DataSource field and as such if both fields are non-empty, they must have the same value. For backwards compatibility, both fields (DataSource and DataSourceRef) will be set to the same value automatically if one of them is empty and the other is non-empty. There are two important differences between DataSource and DataSourceRef: * While DataSource only allows two specific types of objects, DataSourceRef allows any non-core object, as well as PersistentVolumeClaim objects. * While DataSource ignores disallowed values (dropping them), DataSourceRef preserves all values, and generates an error if a disallowed value is specified. (Beta) Using this field requires the AnyVolumeDataSource feature gate to be enabled.",
                                                                                    "properties": {
                                                                                        "apiGroup": {
                                                                                            "description": "APIGroup is the group for the resource being referenced. If APIGroup is not specified, the specified Kind must be in the core API group. For any other third-party types, APIGroup is required.",
                                                                                            "type": "string",
                                                                                        },
                                                                                        "kind": {
                                                                                            "description": "Kind is the type of resource being referenced",
                                                                                            "type": "string",
                                                                                        },
                                                                                        "name": {
                                                                                            "description": "Name is the name of resource being referenced",
                                                                                            "type": "string",
                                                                                        },
                                                                                    },
                                                                                    "required": [
                                                                                        "kind",
                                                                                        "name",
                                                                                    ],
                                                                                    "type": "object",
                                                                                    "x-kubernetes-map-type": "atomic",
                                                                                },
                                                                                "resources": {
                                                                                    "description": "resources represents the minimum resources the volume should have. If RecoverVolumeExpansionFailure feature is enabled users are allowed to specify resource requirements that are lower than previous value but must still be higher than capacity recorded in the status field of the claim. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#resources",
                                                                                    "properties": {
                                                                                        "limits": {
                                                                                            "additionalProperties": {
                                                                                                "anyOf": [
                                                                                                    {
                                                                                                        "type": "integer"
                                                                                                    },
                                                                                                    {
                                                                                                        "type": "string"
                                                                                                    },
                                                                                                ],
                                                                                                "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                                                "x-kubernetes-int-or-string": True,
                                                                                            },
                                                                                            "description": "Limits describes the maximum amount of compute resources allowed. More info: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/",
                                                                                            "type": "object",
                                                                                        },
                                                                                        "requests": {
                                                                                            "additionalProperties": {
                                                                                                "anyOf": [
                                                                                                    {
                                                                                                        "type": "integer"
                                                                                                    },
                                                                                                    {
                                                                                                        "type": "string"
                                                                                                    },
                                                                                                ],
                                                                                                "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                                                "x-kubernetes-int-or-string": True,
                                                                                            },
                                                                                            "description": "Requests describes the minimum amount of compute resources required. If Requests is omitted for a container, it defaults to Limits if that is explicitly specified, otherwise to an implementation-defined value. More info: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/",
                                                                                            "type": "object",
                                                                                        },
                                                                                    },
                                                                                    "type": "object",
                                                                                },
                                                                                "selector": {
                                                                                    "description": "selector is a label query over volumes to consider for binding.",
                                                                                    "properties": {
                                                                                        "matchExpressions": {
                                                                                            "description": "matchExpressions is a list of label selector requirements. The requirements are ANDed.",
                                                                                            "items": {
                                                                                                "description": "A label selector requirement is a selector that contains values, a key, and an operator that relates the key and values.",
                                                                                                "properties": {
                                                                                                    "key": {
                                                                                                        "description": "key is the label key that the selector applies to.",
                                                                                                        "type": "string",
                                                                                                    },
                                                                                                    "operator": {
                                                                                                        "description": "operator represents a key's relationship to a set of values. Valid operators are In, NotIn, Exists and DoesNotExist.",
                                                                                                        "type": "string",
                                                                                                    },
                                                                                                    "values": {
                                                                                                        "description": "values is an array of string values. If the operator is In or NotIn, the values array must be non-empty. If the operator is Exists or DoesNotExist, the values array must be empty. This array is replaced during a strategic merge patch.",
                                                                                                        "items": {
                                                                                                            "type": "string"
                                                                                                        },
                                                                                                        "type": "array",
                                                                                                    },
                                                                                                },
                                                                                                "required": [
                                                                                                    "key",
                                                                                                    "operator",
                                                                                                ],
                                                                                                "type": "object",
                                                                                            },
                                                                                            "type": "array",
                                                                                        },
                                                                                        "matchLabels": {
                                                                                            "additionalProperties": {
                                                                                                "type": "string"
                                                                                            },
                                                                                            "description": 'matchLabels is a map of {key,value} pairs. A single {key,value} in the matchLabels map is equivalent to an element of matchExpressions, whose key field is "key", the operator is "In", and the values array contains only "value". The requirements are ANDed.',
                                                                                            "type": "object",
                                                                                        },
                                                                                    },
                                                                                    "type": "object",
                                                                                    "x-kubernetes-map-type": "atomic",
                                                                                },
                                                                                "storageClassName": {
                                                                                    "description": "storageClassName is the name of the StorageClass required by the claim. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#class-1",
                                                                                    "type": "string",
                                                                                },
                                                                                "volumeMode": {
                                                                                    "description": "volumeMode defines what type of volume is required by the claim. Value of Filesystem is implied when not included in claim spec.",
                                                                                    "type": "string",
                                                                                },
                                                                                "volumeName": {
                                                                                    "description": "volumeName is the binding reference to the PersistentVolume backing this claim.",
                                                                                    "type": "string",
                                                                                },
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "status": {
                                                                            "description": "status represents the current information/status of a persistent volume claim. Read-only. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#persistentvolumeclaims",
                                                                            "properties": {
                                                                                "accessModes": {
                                                                                    "description": "accessModes contains the actual access modes the volume backing the PVC has. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#access-modes-1",
                                                                                    "items": {
                                                                                        "type": "string"
                                                                                    },
                                                                                    "type": "array",
                                                                                },
                                                                                "allocatedResources": {
                                                                                    "additionalProperties": {
                                                                                        "anyOf": [
                                                                                            {
                                                                                                "type": "integer"
                                                                                            },
                                                                                            {
                                                                                                "type": "string"
                                                                                            },
                                                                                        ],
                                                                                        "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                                        "x-kubernetes-int-or-string": True,
                                                                                    },
                                                                                    "description": "allocatedResources is the storage resource within AllocatedResources tracks the capacity allocated to a PVC. It may be larger than the actual capacity when a volume expansion operation is requested. For storage quota, the larger value from allocatedResources and PVC.spec.resources is used. If allocatedResources is not set, PVC.spec.resources alone is used for quota calculation. If a volume expansion capacity request is lowered, allocatedResources is only lowered if there are no expansion operations in progress and if the actual volume capacity is equal or lower than the requested capacity. This is an alpha field and requires enabling RecoverVolumeExpansionFailure feature.",
                                                                                    "type": "object",
                                                                                },
                                                                                "capacity": {
                                                                                    "additionalProperties": {
                                                                                        "anyOf": [
                                                                                            {
                                                                                                "type": "integer"
                                                                                            },
                                                                                            {
                                                                                                "type": "string"
                                                                                            },
                                                                                        ],
                                                                                        "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                                        "x-kubernetes-int-or-string": True,
                                                                                    },
                                                                                    "description": "capacity represents the actual resources of the underlying volume.",
                                                                                    "type": "object",
                                                                                },
                                                                                "conditions": {
                                                                                    "description": "conditions is the current Condition of persistent volume claim. If underlying persistent volume is being resized then the Condition will be set to 'ResizeStarted'.",
                                                                                    "items": {
                                                                                        "description": "PersistentVolumeClaimCondition contails details about state of pvc",
                                                                                        "properties": {
                                                                                            "lastProbeTime": {
                                                                                                "description": "lastProbeTime is the time we probed the condition.",
                                                                                                "format": "date-time",
                                                                                                "type": "string",
                                                                                            },
                                                                                            "lastTransitionTime": {
                                                                                                "description": "lastTransitionTime is the time the condition transitioned from one status to another.",
                                                                                                "format": "date-time",
                                                                                                "type": "string",
                                                                                            },
                                                                                            "message": {
                                                                                                "description": "message is the human-readable message indicating details about last transition.",
                                                                                                "type": "string",
                                                                                            },
                                                                                            "reason": {
                                                                                                "description": 'reason is a unique, this should be a short, machine understandable string that gives the reason for condition\'s last transition. If it reports "ResizeStarted" that means the underlying persistent volume is being resized.',
                                                                                                "type": "string",
                                                                                            },
                                                                                            "status": {
                                                                                                "type": "string"
                                                                                            },
                                                                                            "type": {
                                                                                                "description": "PersistentVolumeClaimConditionType is a valid value of PersistentVolumeClaimCondition.Type",
                                                                                                "type": "string",
                                                                                            },
                                                                                        },
                                                                                        "required": [
                                                                                            "status",
                                                                                            "type",
                                                                                        ],
                                                                                        "type": "object",
                                                                                    },
                                                                                    "type": "array",
                                                                                },
                                                                                "phase": {
                                                                                    "description": "phase represents the current phase of PersistentVolumeClaim.",
                                                                                    "type": "string",
                                                                                },
                                                                                "resizeStatus": {
                                                                                    "description": "resizeStatus stores status of resize operation. ResizeStatus is not set by default but when expansion is complete resizeStatus is set to empty string by resize controller or kubelet. This is an alpha field and requires enabling RecoverVolumeExpansionFailure feature.",
                                                                                    "type": "string",
                                                                                },
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "type": "array",
                                                            },
                                                        },
                                                        "required": ["name"],
                                                        "type": "object",
                                                    },
                                                    "minItems": 1,
                                                    "type": "array",
                                                },
                                                "podDisruptionBudget": {
                                                    "description": "PodDisruptionBudget provides access to the default pod disruption budget for the Elasticsearch cluster. The default budget selects all cluster pods and sets `maxUnavailable` to 1. To disable, set `PodDisruptionBudget` to the empty value (`{}` in YAML).",
                                                    "properties": {
                                                        "metadata": {
                                                            "description": "ObjectMeta is the metadata of the PDB. The name and namespace provided here are managed by ECK and will be ignored.",
                                                            "properties": {
                                                                "annotations": {
                                                                    "additionalProperties": {
                                                                        "type": "string"
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "finalizers": {
                                                                    "items": {
                                                                        "type": "string"
                                                                    },
                                                                    "type": "array",
                                                                },
                                                                "labels": {
                                                                    "additionalProperties": {
                                                                        "type": "string"
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "name": {
                                                                    "type": "string"
                                                                },
                                                                "namespace": {
                                                                    "type": "string"
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                        "spec": {
                                                            "description": "Spec is the specification of the PDB.",
                                                            "properties": {
                                                                "maxUnavailable": {
                                                                    "anyOf": [
                                                                        {
                                                                            "type": "integer"
                                                                        },
                                                                        {
                                                                            "type": "string"
                                                                        },
                                                                    ],
                                                                    "description": 'An eviction is allowed if at most "maxUnavailable" pods selected by "selector" are unavailable after the eviction, i.e. even in absence of the evicted pod. For example, one can prevent all voluntary evictions by specifying 0. This is a mutually exclusive setting with "minAvailable".',
                                                                    "x-kubernetes-int-or-string": True,
                                                                },
                                                                "minAvailable": {
                                                                    "anyOf": [
                                                                        {
                                                                            "type": "integer"
                                                                        },
                                                                        {
                                                                            "type": "string"
                                                                        },
                                                                    ],
                                                                    "description": 'An eviction is allowed if at least "minAvailable" pods selected by "selector" will still be available after the eviction, i.e. even in the absence of the evicted pod.  So for example you can prevent all voluntary evictions by specifying "100%".',
                                                                    "x-kubernetes-int-or-string": True,
                                                                },
                                                                "selector": {
                                                                    "description": "Label query over pods whose evictions are managed by the disruption budget. A null selector will match no pods, while an empty ({}) selector will select all pods within the namespace.",
                                                                    "properties": {
                                                                        "matchExpressions": {
                                                                            "description": "matchExpressions is a list of label selector requirements. The requirements are ANDed.",
                                                                            "items": {
                                                                                "description": "A label selector requirement is a selector that contains values, a key, and an operator that relates the key and values.",
                                                                                "properties": {
                                                                                    "key": {
                                                                                        "description": "key is the label key that the selector applies to.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "operator": {
                                                                                        "description": "operator represents a key's relationship to a set of values. Valid operators are In, NotIn, Exists and DoesNotExist.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "values": {
                                                                                        "description": "values is an array of string values. If the operator is In or NotIn, the values array must be non-empty. If the operator is Exists or DoesNotExist, the values array must be empty. This array is replaced during a strategic merge patch.",
                                                                                        "items": {
                                                                                            "type": "string"
                                                                                        },
                                                                                        "type": "array",
                                                                                    },
                                                                                },
                                                                                "required": [
                                                                                    "key",
                                                                                    "operator",
                                                                                ],
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "matchLabels": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "description": 'matchLabels is a map of {key,value} pairs. A single {key,value} in the matchLabels map is equivalent to an element of matchExpressions, whose key field is "key", the operator is "In", and the values array contains only "value". The requirements are ANDed.',
                                                                            "type": "object",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                    "x-kubernetes-map-type": "atomic",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "remoteClusters": {
                                                    "description": "RemoteClusters enables you to establish uni-directional connections to a remote Elasticsearch cluster.",
                                                    "items": {
                                                        "description": "RemoteCluster declares a remote Elasticsearch cluster connection.",
                                                        "properties": {
                                                            "elasticsearchRef": {
                                                                "description": "ElasticsearchRef is a reference to an Elasticsearch cluster running within the same k8s cluster.",
                                                                "properties": {
                                                                    "name": {
                                                                        "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                                        "type": "string",
                                                                    },
                                                                    "namespace": {
                                                                        "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                                        "type": "string",
                                                                    },
                                                                    "serviceName": {
                                                                        "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                                        "type": "string",
                                                                    },
                                                                },
                                                                "type": "object",
                                                            },
                                                            "name": {
                                                                "description": "Name is the name of the remote cluster as it is set in the Elasticsearch settings. The name is expected to be unique for each remote clusters.",
                                                                "minLength": 1,
                                                                "type": "string",
                                                            },
                                                        },
                                                        "required": ["name"],
                                                        "type": "object",
                                                    },
                                                    "type": "array",
                                                },
                                                "revisionHistoryLimit": {
                                                    "description": "RevisionHistoryLimit is the number of revisions to retain to allow rollback in the underlying StatefulSets.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "secureSettings": {
                                                    "description": "SecureSettings is a list of references to Kubernetes secrets containing sensitive configuration options for Elasticsearch.",
                                                    "items": {
                                                        "description": "SecretSource defines a data source based on a Kubernetes Secret.",
                                                        "properties": {
                                                            "entries": {
                                                                "description": "Entries define how to project each key-value pair in the secret to filesystem paths. If not defined, all keys will be projected to similarly named paths in the filesystem. If defined, only the specified keys will be projected to the corresponding paths.",
                                                                "items": {
                                                                    "description": "KeyToPath defines how to map a key in a Secret object to a filesystem path.",
                                                                    "properties": {
                                                                        "key": {
                                                                            "description": "Key is the key contained in the secret.",
                                                                            "type": "string",
                                                                        },
                                                                        "path": {
                                                                            "description": 'Path is the relative file path to map the key to. Path must not be an absolute file path and must not contain any ".." components.',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "required": ["key"],
                                                                    "type": "object",
                                                                },
                                                                "type": "array",
                                                            },
                                                            "secretName": {
                                                                "description": "SecretName is the name of the secret.",
                                                                "type": "string",
                                                            },
                                                        },
                                                        "required": ["secretName"],
                                                        "type": "object",
                                                    },
                                                    "type": "array",
                                                },
                                                "serviceAccountName": {
                                                    "description": "ServiceAccountName is used to check access from the current resource to a resource (for ex. a remote Elasticsearch cluster) in a different namespace. Can only be used if ECK is enforcing RBAC on references.",
                                                    "type": "string",
                                                },
                                                "transport": {
                                                    "description": "Transport holds transport layer settings for Elasticsearch.",
                                                    "properties": {
                                                        "service": {
                                                            "description": "Service defines the template for the associated Kubernetes Service object.",
                                                            "properties": {
                                                                "metadata": {
                                                                    "description": "ObjectMeta is the metadata of the service. The name and namespace provided here are managed by ECK and will be ignored.",
                                                                    "properties": {
                                                                        "annotations": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "finalizers": {
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "labels": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "name": {
                                                                            "type": "string"
                                                                        },
                                                                        "namespace": {
                                                                            "type": "string"
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "spec": {
                                                                    "description": "Spec is the specification of the service.",
                                                                    "properties": {
                                                                        "allocateLoadBalancerNodePorts": {
                                                                            "description": 'allocateLoadBalancerNodePorts defines if NodePorts will be automatically allocated for services with type LoadBalancer.  Default is "true". It may be set to "false" if the cluster load-balancer does not rely on NodePorts.  If the caller requests specific NodePorts (by specifying a value), those requests will be respected, regardless of this field. This field may only be set for services with type LoadBalancer and will be cleared if the type is changed to any other type.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "clusterIP": {
                                                                            "description": 'clusterIP is the IP address of the service and is usually assigned randomly. If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be blank) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address. Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "clusterIPs": {
                                                                            "description": 'ClusterIPs is a list of IP addresses assigned to this service, and are usually assigned randomly.  If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be empty) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address.  Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName.  If this field is not specified, it will be initialized from the clusterIP field.  If this field is specified, clients must ensure that clusterIPs[0] and clusterIP have the same value. \n This field may hold a maximum of two entries (dual-stack IPs, in either order). These IPs must correspond to the values of the ipFamilies field. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "externalIPs": {
                                                                            "description": "externalIPs is a list of IP addresses for which nodes in the cluster will also accept traffic for this service.  These IPs are not managed by Kubernetes.  The user is responsible for ensuring that traffic arrives at a node with this IP.  A common example is external load-balancers that are not part of the Kubernetes system.",
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "externalName": {
                                                                            "description": 'externalName is the external reference that discovery mechanisms will return as an alias for this service (e.g. a DNS CNAME record). No proxying will be involved.  Must be a lowercase RFC-1123 hostname (https://tools.ietf.org/html/rfc1123) and requires `type` to be "ExternalName".',
                                                                            "type": "string",
                                                                        },
                                                                        "externalTrafficPolicy": {
                                                                            "description": 'externalTrafficPolicy describes how nodes distribute service traffic they receive on one of the Service\'s "externally-facing" addresses (NodePorts, ExternalIPs, and LoadBalancer IPs). If set to "Local", the proxy will configure the service in a way that assumes that external load balancers will take care of balancing the service traffic between nodes, and so each node will deliver traffic only to the node-local endpoints of the service, without masquerading the client source IP. (Traffic mistakenly sent to a node with no endpoints will be dropped.) The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features). Note that traffic sent to an External IP or LoadBalancer IP from within the cluster will always get "Cluster" semantics, but clients sending to a NodePort from within the cluster may need to take traffic policy into account when picking a node.',
                                                                            "type": "string",
                                                                        },
                                                                        "healthCheckNodePort": {
                                                                            "description": "healthCheckNodePort specifies the healthcheck nodePort for the service. This only applies when type is set to LoadBalancer and externalTrafficPolicy is set to Local. If a value is specified, is in-range, and is not in use, it will be used.  If not specified, a value will be automatically allocated.  External systems (e.g. load-balancers) can use this port to determine if a given node holds endpoints for this service or not.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type). This field cannot be updated once set.",
                                                                            "format": "int32",
                                                                            "type": "integer",
                                                                        },
                                                                        "internalTrafficPolicy": {
                                                                            "description": 'InternalTrafficPolicy describes how nodes distribute service traffic they receive on the ClusterIP. If set to "Local", the proxy will assume that pods only want to talk to endpoints of the service on the same node as the pod, dropping the traffic if there are no local endpoints. The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features).',
                                                                            "type": "string",
                                                                        },
                                                                        "ipFamilies": {
                                                                            "description": 'IPFamilies is a list of IP families (e.g. IPv4, IPv6) assigned to this service. This field is usually assigned automatically based on cluster configuration and the ipFamilyPolicy field. If this field is specified manually, the requested family is available in the cluster, and ipFamilyPolicy allows it, it will be used; otherwise creation of the service will fail. This field is conditionally mutable: it allows for adding or removing a secondary IP family, but it does not allow changing the primary IP family of the Service. Valid values are "IPv4" and "IPv6".  This field only applies to Services of types ClusterIP, NodePort, and LoadBalancer, and does apply to "headless" services. This field will be wiped when updating a Service to type ExternalName. \n This field may hold a maximum of two entries (dual-stack families, in either order).  These families must correspond to the values of the clusterIPs field, if specified. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field.',
                                                                            "items": {
                                                                                "description": "IPFamily represents the IP Family (IPv4 or IPv6). This type is used to express the family of an IP expressed by a type (e.g. service.spec.ipFamilies).",
                                                                                "type": "string",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "ipFamilyPolicy": {
                                                                            "description": 'IPFamilyPolicy represents the dual-stack-ness requested or required by this Service. If there is no value provided, then this field will be set to SingleStack. Services can be "SingleStack" (a single IP family), "PreferDualStack" (two IP families on dual-stack configured clusters or a single IP family on single-stack clusters), or "RequireDualStack" (two IP families on dual-stack configured clusters, otherwise fail). The ipFamilies and clusterIPs fields depend on the value of this field. This field will be wiped when updating a service to type ExternalName.',
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerClass": {
                                                                            "description": "loadBalancerClass is the class of the load balancer implementation this Service belongs to. If specified, the value of this field must be a label-style identifier, with an optional prefix, e.g. \"internal-vip\" or \"example.com/internal-vip\". Unprefixed names are reserved for end-users. This field can only be set when the Service type is 'LoadBalancer'. If not set, the default load balancer implementation is used, today this is typically done through the cloud provider integration, but should apply for any default implementation. If set, it is assumed that a load balancer implementation is watching for Services with a matching class. Any default load balancer implementation (e.g. cloud providers) should ignore Services that set this field. This field can only be set when creating or updating a Service to type 'LoadBalancer'. Once set, it can not be changed. This field will be wiped when a service is updated to a non 'LoadBalancer' type.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerIP": {
                                                                            "description": "Only applies to Service Type: LoadBalancer. This feature depends on whether the underlying cloud-provider supports specifying the loadBalancerIP when a load balancer is created. This field will be ignored if the cloud-provider does not support the feature. Deprecated: This field was under-specified and its meaning varies across implementations, and it cannot support dual-stack. As of Kubernetes v1.24, users are encouraged to use implementation-specific annotations when available. This field may be removed in a future API version.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerSourceRanges": {
                                                                            "description": 'If specified and supported by the platform, this will restrict traffic through the cloud-provider load-balancer will be restricted to the specified client IPs. This field will be ignored if the cloud-provider does not support the feature." More info: https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "ports": {
                                                                            "description": "The list of ports that are exposed by this service. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies",
                                                                            "items": {
                                                                                "description": "ServicePort contains information on service's port.",
                                                                                "properties": {
                                                                                    "appProtocol": {
                                                                                        "description": "The application protocol for this port. This field follows standard Kubernetes label syntax. Un-prefixed names are reserved for IANA standard service names (as per RFC-6335 and https://www.iana.org/assignments/service-names). Non-standard protocols should use prefixed names such as mycompany.com/my-custom-protocol.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "name": {
                                                                                        "description": "The name of this port within the service. This must be a DNS_LABEL. All ports within a ServiceSpec must have unique names. When considering the endpoints for a Service, this must match the 'name' field in the EndpointPort. Optional if only one ServicePort is defined on this service.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "nodePort": {
                                                                                        "description": "The port on each node on which this service is exposed when type is NodePort or LoadBalancer.  Usually assigned by the system. If a value is specified, in-range, and not in use it will be used, otherwise the operation will fail.  If not specified, a port will be allocated if this Service requires one.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type from NodePort to ClusterIP). More info: https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "port": {
                                                                                        "description": "The port that will be exposed by this service.",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "protocol": {
                                                                                        "default": "TCP",
                                                                                        "description": 'The IP protocol for this port. Supports "TCP", "UDP", and "SCTP". Default is TCP.',
                                                                                        "type": "string",
                                                                                    },
                                                                                    "targetPort": {
                                                                                        "anyOf": [
                                                                                            {
                                                                                                "type": "integer"
                                                                                            },
                                                                                            {
                                                                                                "type": "string"
                                                                                            },
                                                                                        ],
                                                                                        "description": "Number or name of the port to access on the pods targeted by the service. Number must be in the range 1 to 65535. Name must be an IANA_SVC_NAME. If this is a string, it will be looked up as a named port in the target Pod's container ports. If this is not specified, the value of the 'port' field is used (an identity map). This field is ignored for services with clusterIP=None, and should be omitted or set equal to the 'port' field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#defining-a-service",
                                                                                        "x-kubernetes-int-or-string": True,
                                                                                    },
                                                                                },
                                                                                "required": [
                                                                                    "port"
                                                                                ],
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-map-keys": [
                                                                                "port",
                                                                                "protocol",
                                                                            ],
                                                                            "x-kubernetes-list-type": "map",
                                                                        },
                                                                        "publishNotReadyAddresses": {
                                                                            "description": 'publishNotReadyAddresses indicates that any agent which deals with endpoints for this Service should disregard any indications of ready/not-ready. The primary use case for setting this field is for a StatefulSet\'s Headless Service to propagate SRV DNS records for its Pods for the purpose of peer discovery. The Kubernetes controllers that generate Endpoints and EndpointSlice resources for Services interpret this to mean that all endpoints are considered "ready" even if the Pods themselves are not. Agents which consume only Kubernetes generated endpoints through the Endpoints or EndpointSlice resources can safely assume this behavior.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "selector": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "description": "Route service traffic to pods with label keys and values matching this selector. If empty or not present, the service is assumed to have an external process managing its endpoints, which Kubernetes will not modify. Only applies to types ClusterIP, NodePort, and LoadBalancer. Ignored if type is ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/",
                                                                            "type": "object",
                                                                            "x-kubernetes-map-type": "atomic",
                                                                        },
                                                                        "sessionAffinity": {
                                                                            "description": 'Supports "ClientIP" and "None". Used to maintain session affinity. Enable client IP based session affinity. Must be ClientIP or None. Defaults to None. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "sessionAffinityConfig": {
                                                                            "description": "sessionAffinityConfig contains the configurations of session affinity.",
                                                                            "properties": {
                                                                                "clientIP": {
                                                                                    "description": "clientIP contains the configurations of Client IP based session affinity.",
                                                                                    "properties": {
                                                                                        "timeoutSeconds": {
                                                                                            "description": 'timeoutSeconds specifies the seconds of ClientIP type session sticky time. The value must be >0 && <=86400(for 1 day) if ServiceAffinity == "ClientIP". Default value is 10800(for 3 hours).',
                                                                                            "format": "int32",
                                                                                            "type": "integer",
                                                                                        }
                                                                                    },
                                                                                    "type": "object",
                                                                                }
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "type": {
                                                                            "description": 'type determines how the Service is exposed. Defaults to ClusterIP. Valid options are ExternalName, ClusterIP, NodePort, and LoadBalancer. "ClusterIP" allocates a cluster-internal IP address for load-balancing to endpoints. Endpoints are determined by the selector or if that is not specified, by manual construction of an Endpoints object or EndpointSlice objects. If clusterIP is "None", no virtual IP is allocated and the endpoints are published as a set of endpoints rather than a virtual IP. "NodePort" builds on ClusterIP and allocates a port on every node which routes to the same endpoints as the clusterIP. "LoadBalancer" builds on NodePort and creates an external load-balancer (if supported in the current cloud) which routes to the same endpoints as the clusterIP. "ExternalName" aliases this service to the specified externalName. Several other fields do not apply to ExternalName services. More info: https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                        "tls": {
                                                            "description": "TLS defines options for configuring TLS on the transport layer.",
                                                            "properties": {
                                                                "certificate": {
                                                                    "description": "Certificate is a reference to a Kubernetes secret that contains the CA certificate and private key for generating node certificates. The referenced secret should contain the following: \n - `ca.crt`: The CA certificate in PEM format. - `ca.key`: The private key for the CA certificate in PEM format.",
                                                                    "properties": {
                                                                        "secretName": {
                                                                            "description": "SecretName is the name of the secret.",
                                                                            "type": "string",
                                                                        }
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "otherNameSuffix": {
                                                                    "description": 'OtherNameSuffix when defined will be prefixed with the Pod name and used as the common name, and the first DNSName, as well as an OtherName required by Elasticsearch in the Subject Alternative Name extension of each Elasticsearch node\'s transport TLS certificate. Example: if set to "node.cluster.local", the generated certificate will have its otherName set to "<pod_name>.node.cluster.local".',
                                                                    "type": "string",
                                                                },
                                                                "subjectAltNames": {
                                                                    "description": "SubjectAlternativeNames is a list of SANs to include in the generated node transport TLS certificates.",
                                                                    "items": {
                                                                        "description": "SubjectAlternativeName represents a SAN entry in a x509 certificate.",
                                                                        "properties": {
                                                                            "dns": {
                                                                                "description": "DNS is the DNS name of the subject.",
                                                                                "type": "string",
                                                                            },
                                                                            "ip": {
                                                                                "description": "IP is the IP address of the subject.",
                                                                                "type": "string",
                                                                            },
                                                                        },
                                                                        "type": "object",
                                                                    },
                                                                    "type": "array",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "updateStrategy": {
                                                    "description": "UpdateStrategy specifies how updates to the cluster should be performed.",
                                                    "properties": {
                                                        "changeBudget": {
                                                            "description": "ChangeBudget defines the constraints to consider when applying changes to the Elasticsearch cluster.",
                                                            "properties": {
                                                                "maxSurge": {
                                                                    "description": "MaxSurge is the maximum number of new pods that can be created exceeding the original number of pods defined in the specification. MaxSurge is only taken into consideration when scaling up. Setting a negative value will disable the restriction. Defaults to unbounded if not specified.",
                                                                    "format": "int32",
                                                                    "type": "integer",
                                                                },
                                                                "maxUnavailable": {
                                                                    "description": "MaxUnavailable is the maximum number of pods that can be unavailable (not ready) during the update due to circumstances under the control of the operator. Setting a negative value will disable this restriction. Defaults to 1 if not specified.",
                                                                    "format": "int32",
                                                                    "type": "integer",
                                                                },
                                                            },
                                                            "type": "object",
                                                        }
                                                    },
                                                    "type": "object",
                                                },
                                                "version": {
                                                    "description": "Version of Elasticsearch.",
                                                    "type": "string",
                                                },
                                                "volumeClaimDeletePolicy": {
                                                    "description": "VolumeClaimDeletePolicy sets the policy for handling deletion of PersistentVolumeClaims for all NodeSets. Possible values are DeleteOnScaledownOnly and DeleteOnScaledownAndClusterDeletion. Defaults to DeleteOnScaledownAndClusterDeletion.",
                                                    "enum": [
                                                        "DeleteOnScaledownOnly",
                                                        "DeleteOnScaledownAndClusterDeletion",
                                                    ],
                                                    "type": "string",
                                                },
                                            },
                                            "required": ["nodeSets", "version"],
                                            "type": "object",
                                        },
                                        "status": {
                                            "description": "ElasticsearchStatus represents the observed state of Elasticsearch.",
                                            "properties": {
                                                "availableNodes": {
                                                    "description": "AvailableNodes is the number of available instances.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "conditions": {
                                                    "description": "Conditions holds the current service state of an Elasticsearch cluster. **This API is in technical preview and may be changed or removed in a future release.**",
                                                    "items": {
                                                        "description": "Condition represents Elasticsearch resource's condition. **This API is in technical preview and may be changed or removed in a future release.**",
                                                        "properties": {
                                                            "lastTransitionTime": {
                                                                "format": "date-time",
                                                                "type": "string",
                                                            },
                                                            "message": {
                                                                "type": "string"
                                                            },
                                                            "status": {
                                                                "type": "string"
                                                            },
                                                            "type": {
                                                                "description": "ConditionType defines the condition of an Elasticsearch resource.",
                                                                "type": "string",
                                                            },
                                                        },
                                                        "required": ["status", "type"],
                                                        "type": "object",
                                                    },
                                                    "type": "array",
                                                },
                                                "health": {
                                                    "description": "ElasticsearchHealth is the health of the cluster as returned by the health API.",
                                                    "type": "string",
                                                },
                                                "inProgressOperations": {
                                                    "description": "InProgressOperations represents changes being applied by the operator to the Elasticsearch cluster. **This API is in technical preview and may be changed or removed in a future release.**",
                                                    "properties": {
                                                        "downscale": {
                                                            "description": "DownscaleOperation provides details about in progress downscale operations. **This API is in technical preview and may be changed or removed in a future release.**",
                                                            "properties": {
                                                                "lastUpdatedTime": {
                                                                    "format": "date-time",
                                                                    "type": "string",
                                                                },
                                                                "nodes": {
                                                                    "description": "Nodes which are scheduled to be removed from the cluster.",
                                                                    "items": {
                                                                        "description": "DownscaledNode provides an overview of in progress changes applied by the operator to remove Elasticsearch nodes from the cluster. **This API is in technical preview and may be changed or removed in a future release.**",
                                                                        "properties": {
                                                                            "explanation": {
                                                                                "description": "Explanation provides details about an in progress node shutdown. It is only available for clusters managed with the Elasticsearch shutdown API.",
                                                                                "type": "string",
                                                                            },
                                                                            "name": {
                                                                                "description": "Name of the Elasticsearch node that should be removed.",
                                                                                "type": "string",
                                                                            },
                                                                            "shutdownStatus": {
                                                                                "description": "Shutdown status as returned by the Elasticsearch shutdown API. If the Elasticsearch shutdown API is not available, the shutdown status is then inferred from the remaining shards on the nodes, as observed by the operator.",
                                                                                "type": "string",
                                                                            },
                                                                        },
                                                                        "required": [
                                                                            "name",
                                                                            "shutdownStatus",
                                                                        ],
                                                                        "type": "object",
                                                                    },
                                                                    "type": "array",
                                                                },
                                                                "stalled": {
                                                                    "description": "Stalled represents a state where no progress can be made. It is only available for clusters managed with the Elasticsearch shutdown API.",
                                                                    "type": "boolean",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                        "upgrade": {
                                                            "description": "UpgradeOperation provides an overview of the pending or in progress changes applied by the operator to update the Elasticsearch nodes in the cluster. **This API is in technical preview and may be changed or removed in a future release.**",
                                                            "properties": {
                                                                "lastUpdatedTime": {
                                                                    "format": "date-time",
                                                                    "type": "string",
                                                                },
                                                                "nodes": {
                                                                    "description": "Nodes that must be restarted for upgrade.",
                                                                    "items": {
                                                                        "description": "UpgradedNode provides details about the status of nodes which are expected to be updated. **This API is in technical preview and may be changed or removed in a future release.**",
                                                                        "properties": {
                                                                            "message": {
                                                                                "description": "Optional message to explain why a node may not be immediately restarted for upgrade.",
                                                                                "type": "string",
                                                                            },
                                                                            "name": {
                                                                                "description": "Name of the Elasticsearch node that should be upgraded.",
                                                                                "type": "string",
                                                                            },
                                                                            "predicate": {
                                                                                "description": "Predicate is the name of the predicate currently preventing this node from being deleted for an upgrade.",
                                                                                "type": "string",
                                                                            },
                                                                            "status": {
                                                                                "description": "Status states if the node is either in the process of being deleted for an upgrade, or blocked by a predicate or another condition stated in the message field.",
                                                                                "type": "string",
                                                                            },
                                                                        },
                                                                        "required": [
                                                                            "name",
                                                                            "status",
                                                                        ],
                                                                        "type": "object",
                                                                    },
                                                                    "type": "array",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                        "upscale": {
                                                            "description": "UpscaleOperation provides an overview of in progress changes applied by the operator to add Elasticsearch nodes to the cluster. **This API is in technical preview and may be changed or removed in a future release.**",
                                                            "properties": {
                                                                "lastUpdatedTime": {
                                                                    "format": "date-time",
                                                                    "type": "string",
                                                                },
                                                                "nodes": {
                                                                    "description": "Nodes expected to be added by the operator.",
                                                                    "items": {
                                                                        "properties": {
                                                                            "message": {
                                                                                "description": "Optional message to explain why a node may not be immediately added.",
                                                                                "type": "string",
                                                                            },
                                                                            "name": {
                                                                                "description": "Name of the Elasticsearch node that should be added to the cluster.",
                                                                                "type": "string",
                                                                            },
                                                                            "status": {
                                                                                "description": "NewNodeStatus states if a new node is being created, or if the upscale is delayed.",
                                                                                "type": "string",
                                                                            },
                                                                        },
                                                                        "required": [
                                                                            "name",
                                                                            "status",
                                                                        ],
                                                                        "type": "object",
                                                                    },
                                                                    "type": "array",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "required": [
                                                        "downscale",
                                                        "upgrade",
                                                        "upscale",
                                                    ],
                                                    "type": "object",
                                                },
                                                "monitoringAssociationStatus": {
                                                    "additionalProperties": {
                                                        "description": "AssociationStatus is the status of an association resource.",
                                                        "type": "string",
                                                    },
                                                    "description": "AssociationStatusMap is the map of association's namespaced name string to its AssociationStatus. For resources that have a single Association of a given type (for ex. single ES reference), this map contains a single entry.",
                                                    "type": "object",
                                                },
                                                "observedGeneration": {
                                                    "description": "ObservedGeneration is the most recent generation observed for this Elasticsearch cluster. It corresponds to the metadata generation, which is updated on mutation by the API Server. If the generation observed in status diverges from the generation in metadata, the Elasticsearch controller has not yet processed the changes contained in the Elasticsearch specification.",
                                                    "format": "int64",
                                                    "type": "integer",
                                                },
                                                "phase": {
                                                    "description": "ElasticsearchOrchestrationPhase is the phase Elasticsearch is in from the controller point of view.",
                                                    "type": "string",
                                                },
                                                "version": {
                                                    "description": "Version of the stack resource currently running. During version upgrades, multiple versions may run in parallel: this value specifies the lowest version currently running.",
                                                    "type": "string",
                                                },
                                            },
                                            "type": "object",
                                        },
                                    },
                                    "type": "object",
                                }
                            },
                            "served": True,
                            "storage": True,
                            "subresources": {"status": {}},
                        },
                        {
                            "additionalPrinterColumns": [
                                {
                                    "jsonPath": ".status.health",
                                    "name": "health",
                                    "type": "string",
                                },
                                {
                                    "description": "Available nodes",
                                    "jsonPath": ".status.availableNodes",
                                    "name": "nodes",
                                    "type": "integer",
                                },
                                {
                                    "description": "Elasticsearch version",
                                    "jsonPath": ".spec.version",
                                    "name": "version",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".status.phase",
                                    "name": "phase",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".metadata.creationTimestamp",
                                    "name": "age",
                                    "type": "date",
                                },
                            ],
                            "name": "v1beta1",
                            "schema": {
                                "openAPIV3Schema": {
                                    "description": "Elasticsearch represents an Elasticsearch resource in a Kubernetes cluster.",
                                    "properties": {
                                        "apiVersion": {
                                            "description": "APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources",
                                            "type": "string",
                                        },
                                        "kind": {
                                            "description": "Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds",
                                            "type": "string",
                                        },
                                        "metadata": {"type": "object"},
                                        "spec": {
                                            "description": "ElasticsearchSpec holds the specification of an Elasticsearch cluster.",
                                            "properties": {
                                                "http": {
                                                    "description": "HTTP holds HTTP layer settings for Elasticsearch.",
                                                    "properties": {
                                                        "service": {
                                                            "description": "Service defines the template for the associated Kubernetes Service object.",
                                                            "properties": {
                                                                "metadata": {
                                                                    "description": "ObjectMeta is the metadata of the service. The name and namespace provided here are managed by ECK and will be ignored.",
                                                                    "properties": {
                                                                        "annotations": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "finalizers": {
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "labels": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "name": {
                                                                            "type": "string"
                                                                        },
                                                                        "namespace": {
                                                                            "type": "string"
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "spec": {
                                                                    "description": "Spec is the specification of the service.",
                                                                    "properties": {
                                                                        "allocateLoadBalancerNodePorts": {
                                                                            "description": 'allocateLoadBalancerNodePorts defines if NodePorts will be automatically allocated for services with type LoadBalancer.  Default is "true". It may be set to "false" if the cluster load-balancer does not rely on NodePorts.  If the caller requests specific NodePorts (by specifying a value), those requests will be respected, regardless of this field. This field may only be set for services with type LoadBalancer and will be cleared if the type is changed to any other type.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "clusterIP": {
                                                                            "description": 'clusterIP is the IP address of the service and is usually assigned randomly. If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be blank) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address. Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "clusterIPs": {
                                                                            "description": 'ClusterIPs is a list of IP addresses assigned to this service, and are usually assigned randomly.  If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be empty) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address.  Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName.  If this field is not specified, it will be initialized from the clusterIP field.  If this field is specified, clients must ensure that clusterIPs[0] and clusterIP have the same value. \n This field may hold a maximum of two entries (dual-stack IPs, in either order). These IPs must correspond to the values of the ipFamilies field. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "externalIPs": {
                                                                            "description": "externalIPs is a list of IP addresses for which nodes in the cluster will also accept traffic for this service.  These IPs are not managed by Kubernetes.  The user is responsible for ensuring that traffic arrives at a node with this IP.  A common example is external load-balancers that are not part of the Kubernetes system.",
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "externalName": {
                                                                            "description": 'externalName is the external reference that discovery mechanisms will return as an alias for this service (e.g. a DNS CNAME record). No proxying will be involved.  Must be a lowercase RFC-1123 hostname (https://tools.ietf.org/html/rfc1123) and requires `type` to be "ExternalName".',
                                                                            "type": "string",
                                                                        },
                                                                        "externalTrafficPolicy": {
                                                                            "description": 'externalTrafficPolicy describes how nodes distribute service traffic they receive on one of the Service\'s "externally-facing" addresses (NodePorts, ExternalIPs, and LoadBalancer IPs). If set to "Local", the proxy will configure the service in a way that assumes that external load balancers will take care of balancing the service traffic between nodes, and so each node will deliver traffic only to the node-local endpoints of the service, without masquerading the client source IP. (Traffic mistakenly sent to a node with no endpoints will be dropped.) The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features). Note that traffic sent to an External IP or LoadBalancer IP from within the cluster will always get "Cluster" semantics, but clients sending to a NodePort from within the cluster may need to take traffic policy into account when picking a node.',
                                                                            "type": "string",
                                                                        },
                                                                        "healthCheckNodePort": {
                                                                            "description": "healthCheckNodePort specifies the healthcheck nodePort for the service. This only applies when type is set to LoadBalancer and externalTrafficPolicy is set to Local. If a value is specified, is in-range, and is not in use, it will be used.  If not specified, a value will be automatically allocated.  External systems (e.g. load-balancers) can use this port to determine if a given node holds endpoints for this service or not.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type). This field cannot be updated once set.",
                                                                            "format": "int32",
                                                                            "type": "integer",
                                                                        },
                                                                        "internalTrafficPolicy": {
                                                                            "description": 'InternalTrafficPolicy describes how nodes distribute service traffic they receive on the ClusterIP. If set to "Local", the proxy will assume that pods only want to talk to endpoints of the service on the same node as the pod, dropping the traffic if there are no local endpoints. The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features).',
                                                                            "type": "string",
                                                                        },
                                                                        "ipFamilies": {
                                                                            "description": 'IPFamilies is a list of IP families (e.g. IPv4, IPv6) assigned to this service. This field is usually assigned automatically based on cluster configuration and the ipFamilyPolicy field. If this field is specified manually, the requested family is available in the cluster, and ipFamilyPolicy allows it, it will be used; otherwise creation of the service will fail. This field is conditionally mutable: it allows for adding or removing a secondary IP family, but it does not allow changing the primary IP family of the Service. Valid values are "IPv4" and "IPv6".  This field only applies to Services of types ClusterIP, NodePort, and LoadBalancer, and does apply to "headless" services. This field will be wiped when updating a Service to type ExternalName. \n This field may hold a maximum of two entries (dual-stack families, in either order).  These families must correspond to the values of the clusterIPs field, if specified. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field.',
                                                                            "items": {
                                                                                "description": "IPFamily represents the IP Family (IPv4 or IPv6). This type is used to express the family of an IP expressed by a type (e.g. service.spec.ipFamilies).",
                                                                                "type": "string",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "ipFamilyPolicy": {
                                                                            "description": 'IPFamilyPolicy represents the dual-stack-ness requested or required by this Service. If there is no value provided, then this field will be set to SingleStack. Services can be "SingleStack" (a single IP family), "PreferDualStack" (two IP families on dual-stack configured clusters or a single IP family on single-stack clusters), or "RequireDualStack" (two IP families on dual-stack configured clusters, otherwise fail). The ipFamilies and clusterIPs fields depend on the value of this field. This field will be wiped when updating a service to type ExternalName.',
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerClass": {
                                                                            "description": "loadBalancerClass is the class of the load balancer implementation this Service belongs to. If specified, the value of this field must be a label-style identifier, with an optional prefix, e.g. \"internal-vip\" or \"example.com/internal-vip\". Unprefixed names are reserved for end-users. This field can only be set when the Service type is 'LoadBalancer'. If not set, the default load balancer implementation is used, today this is typically done through the cloud provider integration, but should apply for any default implementation. If set, it is assumed that a load balancer implementation is watching for Services with a matching class. Any default load balancer implementation (e.g. cloud providers) should ignore Services that set this field. This field can only be set when creating or updating a Service to type 'LoadBalancer'. Once set, it can not be changed. This field will be wiped when a service is updated to a non 'LoadBalancer' type.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerIP": {
                                                                            "description": "Only applies to Service Type: LoadBalancer. This feature depends on whether the underlying cloud-provider supports specifying the loadBalancerIP when a load balancer is created. This field will be ignored if the cloud-provider does not support the feature. Deprecated: This field was under-specified and its meaning varies across implementations, and it cannot support dual-stack. As of Kubernetes v1.24, users are encouraged to use implementation-specific annotations when available. This field may be removed in a future API version.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerSourceRanges": {
                                                                            "description": 'If specified and supported by the platform, this will restrict traffic through the cloud-provider load-balancer will be restricted to the specified client IPs. This field will be ignored if the cloud-provider does not support the feature." More info: https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "ports": {
                                                                            "description": "The list of ports that are exposed by this service. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies",
                                                                            "items": {
                                                                                "description": "ServicePort contains information on service's port.",
                                                                                "properties": {
                                                                                    "appProtocol": {
                                                                                        "description": "The application protocol for this port. This field follows standard Kubernetes label syntax. Un-prefixed names are reserved for IANA standard service names (as per RFC-6335 and https://www.iana.org/assignments/service-names). Non-standard protocols should use prefixed names such as mycompany.com/my-custom-protocol.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "name": {
                                                                                        "description": "The name of this port within the service. This must be a DNS_LABEL. All ports within a ServiceSpec must have unique names. When considering the endpoints for a Service, this must match the 'name' field in the EndpointPort. Optional if only one ServicePort is defined on this service.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "nodePort": {
                                                                                        "description": "The port on each node on which this service is exposed when type is NodePort or LoadBalancer.  Usually assigned by the system. If a value is specified, in-range, and not in use it will be used, otherwise the operation will fail.  If not specified, a port will be allocated if this Service requires one.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type from NodePort to ClusterIP). More info: https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "port": {
                                                                                        "description": "The port that will be exposed by this service.",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "protocol": {
                                                                                        "default": "TCP",
                                                                                        "description": 'The IP protocol for this port. Supports "TCP", "UDP", and "SCTP". Default is TCP.',
                                                                                        "type": "string",
                                                                                    },
                                                                                    "targetPort": {
                                                                                        "anyOf": [
                                                                                            {
                                                                                                "type": "integer"
                                                                                            },
                                                                                            {
                                                                                                "type": "string"
                                                                                            },
                                                                                        ],
                                                                                        "description": "Number or name of the port to access on the pods targeted by the service. Number must be in the range 1 to 65535. Name must be an IANA_SVC_NAME. If this is a string, it will be looked up as a named port in the target Pod's container ports. If this is not specified, the value of the 'port' field is used (an identity map). This field is ignored for services with clusterIP=None, and should be omitted or set equal to the 'port' field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#defining-a-service",
                                                                                        "x-kubernetes-int-or-string": True,
                                                                                    },
                                                                                },
                                                                                "required": [
                                                                                    "port"
                                                                                ],
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-map-keys": [
                                                                                "port",
                                                                                "protocol",
                                                                            ],
                                                                            "x-kubernetes-list-type": "map",
                                                                        },
                                                                        "publishNotReadyAddresses": {
                                                                            "description": 'publishNotReadyAddresses indicates that any agent which deals with endpoints for this Service should disregard any indications of ready/not-ready. The primary use case for setting this field is for a StatefulSet\'s Headless Service to propagate SRV DNS records for its Pods for the purpose of peer discovery. The Kubernetes controllers that generate Endpoints and EndpointSlice resources for Services interpret this to mean that all endpoints are considered "ready" even if the Pods themselves are not. Agents which consume only Kubernetes generated endpoints through the Endpoints or EndpointSlice resources can safely assume this behavior.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "selector": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "description": "Route service traffic to pods with label keys and values matching this selector. If empty or not present, the service is assumed to have an external process managing its endpoints, which Kubernetes will not modify. Only applies to types ClusterIP, NodePort, and LoadBalancer. Ignored if type is ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/",
                                                                            "type": "object",
                                                                            "x-kubernetes-map-type": "atomic",
                                                                        },
                                                                        "sessionAffinity": {
                                                                            "description": 'Supports "ClientIP" and "None". Used to maintain session affinity. Enable client IP based session affinity. Must be ClientIP or None. Defaults to None. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "sessionAffinityConfig": {
                                                                            "description": "sessionAffinityConfig contains the configurations of session affinity.",
                                                                            "properties": {
                                                                                "clientIP": {
                                                                                    "description": "clientIP contains the configurations of Client IP based session affinity.",
                                                                                    "properties": {
                                                                                        "timeoutSeconds": {
                                                                                            "description": 'timeoutSeconds specifies the seconds of ClientIP type session sticky time. The value must be >0 && <=86400(for 1 day) if ServiceAffinity == "ClientIP". Default value is 10800(for 3 hours).',
                                                                                            "format": "int32",
                                                                                            "type": "integer",
                                                                                        }
                                                                                    },
                                                                                    "type": "object",
                                                                                }
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "type": {
                                                                            "description": 'type determines how the Service is exposed. Defaults to ClusterIP. Valid options are ExternalName, ClusterIP, NodePort, and LoadBalancer. "ClusterIP" allocates a cluster-internal IP address for load-balancing to endpoints. Endpoints are determined by the selector or if that is not specified, by manual construction of an Endpoints object or EndpointSlice objects. If clusterIP is "None", no virtual IP is allocated and the endpoints are published as a set of endpoints rather than a virtual IP. "NodePort" builds on ClusterIP and allocates a port on every node which routes to the same endpoints as the clusterIP. "LoadBalancer" builds on NodePort and creates an external load-balancer (if supported in the current cloud) which routes to the same endpoints as the clusterIP. "ExternalName" aliases this service to the specified externalName. Several other fields do not apply to ExternalName services. More info: https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                        "tls": {
                                                            "description": "TLS defines options for configuring TLS for HTTP.",
                                                            "properties": {
                                                                "certificate": {
                                                                    "description": "Certificate is a reference to a Kubernetes secret that contains the certificate and private key for enabling TLS. The referenced secret should contain the following: \n - `ca.crt`: The certificate authority (optional). - `tls.crt`: The certificate (or a chain). - `tls.key`: The private key to the first certificate in the certificate chain.",
                                                                    "properties": {
                                                                        "secretName": {
                                                                            "description": "SecretName is the name of the secret.",
                                                                            "type": "string",
                                                                        }
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "selfSignedCertificate": {
                                                                    "description": "SelfSignedCertificate allows configuring the self-signed certificate generated by the operator.",
                                                                    "properties": {
                                                                        "disabled": {
                                                                            "description": "Disabled indicates that the provisioning of the self-signed certifcate should be disabled.",
                                                                            "type": "boolean",
                                                                        },
                                                                        "subjectAltNames": {
                                                                            "description": "SubjectAlternativeNames is a list of SANs to include in the generated HTTP TLS certificate.",
                                                                            "items": {
                                                                                "description": "SubjectAlternativeName represents a SAN entry in a x509 certificate.",
                                                                                "properties": {
                                                                                    "dns": {
                                                                                        "description": "DNS is the DNS name of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "ip": {
                                                                                        "description": "IP is the IP address of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                },
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "image": {
                                                    "description": "Image is the Elasticsearch Docker image to deploy.",
                                                    "type": "string",
                                                },
                                                "nodeSets": {
                                                    "description": "NodeSets allow specifying groups of Elasticsearch nodes sharing the same configuration and Pod templates.",
                                                    "items": {
                                                        "description": "NodeSet is the specification for a group of Elasticsearch nodes sharing the same configuration and a Pod template.",
                                                        "properties": {
                                                            "config": {
                                                                "description": "Config holds the Elasticsearch configuration.",
                                                                "type": "object",
                                                            },
                                                            "count": {
                                                                "description": "Count of Elasticsearch nodes to deploy.",
                                                                "format": "int32",
                                                                "minimum": 1,
                                                                "type": "integer",
                                                            },
                                                            "name": {
                                                                "description": "Name of this set of nodes. Becomes a part of the Elasticsearch node.name setting.",
                                                                "maxLength": 23,
                                                                "pattern": "[a-zA-Z0-9-]+",
                                                                "type": "string",
                                                            },
                                                            "podTemplate": {
                                                                "description": "PodTemplate provides customisation options (labels, annotations, affinity rules, resource requests, and so on) for the Pods belonging to this NodeSet.",
                                                                "type": "object",
                                                            },
                                                            "volumeClaimTemplates": {
                                                                "description": "VolumeClaimTemplates is a list of persistent volume claims to be used by each Pod in this NodeSet. Every claim in this list must have a matching volumeMount in one of the containers defined in the PodTemplate. Items defined here take precedence over any default claims added by the operator with the same name.",
                                                                "items": {
                                                                    "description": "PersistentVolumeClaim is a user's request for and claim to a persistent volume",
                                                                    "properties": {
                                                                        "apiVersion": {
                                                                            "description": "APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources",
                                                                            "type": "string",
                                                                        },
                                                                        "kind": {
                                                                            "description": "Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds",
                                                                            "type": "string",
                                                                        },
                                                                        "metadata": {
                                                                            "description": "Standard object's metadata. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#metadata",
                                                                            "properties": {
                                                                                "annotations": {
                                                                                    "additionalProperties": {
                                                                                        "type": "string"
                                                                                    },
                                                                                    "type": "object",
                                                                                },
                                                                                "finalizers": {
                                                                                    "items": {
                                                                                        "type": "string"
                                                                                    },
                                                                                    "type": "array",
                                                                                },
                                                                                "labels": {
                                                                                    "additionalProperties": {
                                                                                        "type": "string"
                                                                                    },
                                                                                    "type": "object",
                                                                                },
                                                                                "name": {
                                                                                    "type": "string"
                                                                                },
                                                                                "namespace": {
                                                                                    "type": "string"
                                                                                },
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "spec": {
                                                                            "description": "spec defines the desired characteristics of a volume requested by a pod author. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#persistentvolumeclaims",
                                                                            "properties": {
                                                                                "accessModes": {
                                                                                    "description": "accessModes contains the desired access modes the volume should have. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#access-modes-1",
                                                                                    "items": {
                                                                                        "type": "string"
                                                                                    },
                                                                                    "type": "array",
                                                                                },
                                                                                "dataSource": {
                                                                                    "description": "dataSource field can be used to specify either: * An existing VolumeSnapshot object (snapshot.storage.k8s.io/VolumeSnapshot) * An existing PVC (PersistentVolumeClaim) If the provisioner or an external controller can support the specified data source, it will create a new volume based on the contents of the specified data source. If the AnyVolumeDataSource feature gate is enabled, this field will always have the same contents as the DataSourceRef field.",
                                                                                    "properties": {
                                                                                        "apiGroup": {
                                                                                            "description": "APIGroup is the group for the resource being referenced. If APIGroup is not specified, the specified Kind must be in the core API group. For any other third-party types, APIGroup is required.",
                                                                                            "type": "string",
                                                                                        },
                                                                                        "kind": {
                                                                                            "description": "Kind is the type of resource being referenced",
                                                                                            "type": "string",
                                                                                        },
                                                                                        "name": {
                                                                                            "description": "Name is the name of resource being referenced",
                                                                                            "type": "string",
                                                                                        },
                                                                                    },
                                                                                    "required": [
                                                                                        "kind",
                                                                                        "name",
                                                                                    ],
                                                                                    "type": "object",
                                                                                    "x-kubernetes-map-type": "atomic",
                                                                                },
                                                                                "dataSourceRef": {
                                                                                    "description": "dataSourceRef specifies the object from which to populate the volume with data, if a non-empty volume is desired. This may be any local object from a non-empty API group (non core object) or a PersistentVolumeClaim object. When this field is specified, volume binding will only succeed if the type of the specified object matches some installed volume populator or dynamic provisioner. This field will replace the functionality of the DataSource field and as such if both fields are non-empty, they must have the same value. For backwards compatibility, both fields (DataSource and DataSourceRef) will be set to the same value automatically if one of them is empty and the other is non-empty. There are two important differences between DataSource and DataSourceRef: * While DataSource only allows two specific types of objects, DataSourceRef allows any non-core object, as well as PersistentVolumeClaim objects. * While DataSource ignores disallowed values (dropping them), DataSourceRef preserves all values, and generates an error if a disallowed value is specified. (Beta) Using this field requires the AnyVolumeDataSource feature gate to be enabled.",
                                                                                    "properties": {
                                                                                        "apiGroup": {
                                                                                            "description": "APIGroup is the group for the resource being referenced. If APIGroup is not specified, the specified Kind must be in the core API group. For any other third-party types, APIGroup is required.",
                                                                                            "type": "string",
                                                                                        },
                                                                                        "kind": {
                                                                                            "description": "Kind is the type of resource being referenced",
                                                                                            "type": "string",
                                                                                        },
                                                                                        "name": {
                                                                                            "description": "Name is the name of resource being referenced",
                                                                                            "type": "string",
                                                                                        },
                                                                                    },
                                                                                    "required": [
                                                                                        "kind",
                                                                                        "name",
                                                                                    ],
                                                                                    "type": "object",
                                                                                    "x-kubernetes-map-type": "atomic",
                                                                                },
                                                                                "resources": {
                                                                                    "description": "resources represents the minimum resources the volume should have. If RecoverVolumeExpansionFailure feature is enabled users are allowed to specify resource requirements that are lower than previous value but must still be higher than capacity recorded in the status field of the claim. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#resources",
                                                                                    "properties": {
                                                                                        "limits": {
                                                                                            "additionalProperties": {
                                                                                                "anyOf": [
                                                                                                    {
                                                                                                        "type": "integer"
                                                                                                    },
                                                                                                    {
                                                                                                        "type": "string"
                                                                                                    },
                                                                                                ],
                                                                                                "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                                                "x-kubernetes-int-or-string": True,
                                                                                            },
                                                                                            "description": "Limits describes the maximum amount of compute resources allowed. More info: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/",
                                                                                            "type": "object",
                                                                                        },
                                                                                        "requests": {
                                                                                            "additionalProperties": {
                                                                                                "anyOf": [
                                                                                                    {
                                                                                                        "type": "integer"
                                                                                                    },
                                                                                                    {
                                                                                                        "type": "string"
                                                                                                    },
                                                                                                ],
                                                                                                "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                                                "x-kubernetes-int-or-string": True,
                                                                                            },
                                                                                            "description": "Requests describes the minimum amount of compute resources required. If Requests is omitted for a container, it defaults to Limits if that is explicitly specified, otherwise to an implementation-defined value. More info: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/",
                                                                                            "type": "object",
                                                                                        },
                                                                                    },
                                                                                    "type": "object",
                                                                                },
                                                                                "selector": {
                                                                                    "description": "selector is a label query over volumes to consider for binding.",
                                                                                    "properties": {
                                                                                        "matchExpressions": {
                                                                                            "description": "matchExpressions is a list of label selector requirements. The requirements are ANDed.",
                                                                                            "items": {
                                                                                                "description": "A label selector requirement is a selector that contains values, a key, and an operator that relates the key and values.",
                                                                                                "properties": {
                                                                                                    "key": {
                                                                                                        "description": "key is the label key that the selector applies to.",
                                                                                                        "type": "string",
                                                                                                    },
                                                                                                    "operator": {
                                                                                                        "description": "operator represents a key's relationship to a set of values. Valid operators are In, NotIn, Exists and DoesNotExist.",
                                                                                                        "type": "string",
                                                                                                    },
                                                                                                    "values": {
                                                                                                        "description": "values is an array of string values. If the operator is In or NotIn, the values array must be non-empty. If the operator is Exists or DoesNotExist, the values array must be empty. This array is replaced during a strategic merge patch.",
                                                                                                        "items": {
                                                                                                            "type": "string"
                                                                                                        },
                                                                                                        "type": "array",
                                                                                                    },
                                                                                                },
                                                                                                "required": [
                                                                                                    "key",
                                                                                                    "operator",
                                                                                                ],
                                                                                                "type": "object",
                                                                                            },
                                                                                            "type": "array",
                                                                                        },
                                                                                        "matchLabels": {
                                                                                            "additionalProperties": {
                                                                                                "type": "string"
                                                                                            },
                                                                                            "description": 'matchLabels is a map of {key,value} pairs. A single {key,value} in the matchLabels map is equivalent to an element of matchExpressions, whose key field is "key", the operator is "In", and the values array contains only "value". The requirements are ANDed.',
                                                                                            "type": "object",
                                                                                        },
                                                                                    },
                                                                                    "type": "object",
                                                                                    "x-kubernetes-map-type": "atomic",
                                                                                },
                                                                                "storageClassName": {
                                                                                    "description": "storageClassName is the name of the StorageClass required by the claim. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#class-1",
                                                                                    "type": "string",
                                                                                },
                                                                                "volumeMode": {
                                                                                    "description": "volumeMode defines what type of volume is required by the claim. Value of Filesystem is implied when not included in claim spec.",
                                                                                    "type": "string",
                                                                                },
                                                                                "volumeName": {
                                                                                    "description": "volumeName is the binding reference to the PersistentVolume backing this claim.",
                                                                                    "type": "string",
                                                                                },
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "status": {
                                                                            "description": "status represents the current information/status of a persistent volume claim. Read-only. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#persistentvolumeclaims",
                                                                            "properties": {
                                                                                "accessModes": {
                                                                                    "description": "accessModes contains the actual access modes the volume backing the PVC has. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#access-modes-1",
                                                                                    "items": {
                                                                                        "type": "string"
                                                                                    },
                                                                                    "type": "array",
                                                                                },
                                                                                "allocatedResources": {
                                                                                    "additionalProperties": {
                                                                                        "anyOf": [
                                                                                            {
                                                                                                "type": "integer"
                                                                                            },
                                                                                            {
                                                                                                "type": "string"
                                                                                            },
                                                                                        ],
                                                                                        "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                                        "x-kubernetes-int-or-string": True,
                                                                                    },
                                                                                    "description": "allocatedResources is the storage resource within AllocatedResources tracks the capacity allocated to a PVC. It may be larger than the actual capacity when a volume expansion operation is requested. For storage quota, the larger value from allocatedResources and PVC.spec.resources is used. If allocatedResources is not set, PVC.spec.resources alone is used for quota calculation. If a volume expansion capacity request is lowered, allocatedResources is only lowered if there are no expansion operations in progress and if the actual volume capacity is equal or lower than the requested capacity. This is an alpha field and requires enabling RecoverVolumeExpansionFailure feature.",
                                                                                    "type": "object",
                                                                                },
                                                                                "capacity": {
                                                                                    "additionalProperties": {
                                                                                        "anyOf": [
                                                                                            {
                                                                                                "type": "integer"
                                                                                            },
                                                                                            {
                                                                                                "type": "string"
                                                                                            },
                                                                                        ],
                                                                                        "pattern": "^(\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\\+|-)?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))))?$",
                                                                                        "x-kubernetes-int-or-string": True,
                                                                                    },
                                                                                    "description": "capacity represents the actual resources of the underlying volume.",
                                                                                    "type": "object",
                                                                                },
                                                                                "conditions": {
                                                                                    "description": "conditions is the current Condition of persistent volume claim. If underlying persistent volume is being resized then the Condition will be set to 'ResizeStarted'.",
                                                                                    "items": {
                                                                                        "description": "PersistentVolumeClaimCondition contails details about state of pvc",
                                                                                        "properties": {
                                                                                            "lastProbeTime": {
                                                                                                "description": "lastProbeTime is the time we probed the condition.",
                                                                                                "format": "date-time",
                                                                                                "type": "string",
                                                                                            },
                                                                                            "lastTransitionTime": {
                                                                                                "description": "lastTransitionTime is the time the condition transitioned from one status to another.",
                                                                                                "format": "date-time",
                                                                                                "type": "string",
                                                                                            },
                                                                                            "message": {
                                                                                                "description": "message is the human-readable message indicating details about last transition.",
                                                                                                "type": "string",
                                                                                            },
                                                                                            "reason": {
                                                                                                "description": 'reason is a unique, this should be a short, machine understandable string that gives the reason for condition\'s last transition. If it reports "ResizeStarted" that means the underlying persistent volume is being resized.',
                                                                                                "type": "string",
                                                                                            },
                                                                                            "status": {
                                                                                                "type": "string"
                                                                                            },
                                                                                            "type": {
                                                                                                "description": "PersistentVolumeClaimConditionType is a valid value of PersistentVolumeClaimCondition.Type",
                                                                                                "type": "string",
                                                                                            },
                                                                                        },
                                                                                        "required": [
                                                                                            "status",
                                                                                            "type",
                                                                                        ],
                                                                                        "type": "object",
                                                                                    },
                                                                                    "type": "array",
                                                                                },
                                                                                "phase": {
                                                                                    "description": "phase represents the current phase of PersistentVolumeClaim.",
                                                                                    "type": "string",
                                                                                },
                                                                                "resizeStatus": {
                                                                                    "description": "resizeStatus stores status of resize operation. ResizeStatus is not set by default but when expansion is complete resizeStatus is set to empty string by resize controller or kubelet. This is an alpha field and requires enabling RecoverVolumeExpansionFailure feature.",
                                                                                    "type": "string",
                                                                                },
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "type": "array",
                                                            },
                                                        },
                                                        "required": ["count", "name"],
                                                        "type": "object",
                                                    },
                                                    "minItems": 1,
                                                    "type": "array",
                                                },
                                                "podDisruptionBudget": {
                                                    "description": "PodDisruptionBudget provides access to the default pod disruption budget for the Elasticsearch cluster. The default budget selects all cluster pods and sets `maxUnavailable` to 1. To disable, set `PodDisruptionBudget` to the empty value (`{}` in YAML).",
                                                    "properties": {
                                                        "metadata": {
                                                            "description": "ObjectMeta is the metadata of the PDB. The name and namespace provided here are managed by ECK and will be ignored.",
                                                            "properties": {
                                                                "annotations": {
                                                                    "additionalProperties": {
                                                                        "type": "string"
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "finalizers": {
                                                                    "items": {
                                                                        "type": "string"
                                                                    },
                                                                    "type": "array",
                                                                },
                                                                "labels": {
                                                                    "additionalProperties": {
                                                                        "type": "string"
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "name": {
                                                                    "type": "string"
                                                                },
                                                                "namespace": {
                                                                    "type": "string"
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                        "spec": {
                                                            "description": "Spec is the specification of the PDB.",
                                                            "properties": {
                                                                "maxUnavailable": {
                                                                    "anyOf": [
                                                                        {
                                                                            "type": "integer"
                                                                        },
                                                                        {
                                                                            "type": "string"
                                                                        },
                                                                    ],
                                                                    "description": 'An eviction is allowed if at most "maxUnavailable" pods selected by "selector" are unavailable after the eviction, i.e. even in absence of the evicted pod. For example, one can prevent all voluntary evictions by specifying 0. This is a mutually exclusive setting with "minAvailable".',
                                                                    "x-kubernetes-int-or-string": True,
                                                                },
                                                                "minAvailable": {
                                                                    "anyOf": [
                                                                        {
                                                                            "type": "integer"
                                                                        },
                                                                        {
                                                                            "type": "string"
                                                                        },
                                                                    ],
                                                                    "description": 'An eviction is allowed if at least "minAvailable" pods selected by "selector" will still be available after the eviction, i.e. even in the absence of the evicted pod.  So for example you can prevent all voluntary evictions by specifying "100%".',
                                                                    "x-kubernetes-int-or-string": True,
                                                                },
                                                                "selector": {
                                                                    "description": "Label query over pods whose evictions are managed by the disruption budget. A null selector selects no pods. An empty selector ({}) also selects no pods, which differs from standard behavior of selecting all pods. In policy/v1, an empty selector will select all pods in the namespace.",
                                                                    "properties": {
                                                                        "matchExpressions": {
                                                                            "description": "matchExpressions is a list of label selector requirements. The requirements are ANDed.",
                                                                            "items": {
                                                                                "description": "A label selector requirement is a selector that contains values, a key, and an operator that relates the key and values.",
                                                                                "properties": {
                                                                                    "key": {
                                                                                        "description": "key is the label key that the selector applies to.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "operator": {
                                                                                        "description": "operator represents a key's relationship to a set of values. Valid operators are In, NotIn, Exists and DoesNotExist.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "values": {
                                                                                        "description": "values is an array of string values. If the operator is In or NotIn, the values array must be non-empty. If the operator is Exists or DoesNotExist, the values array must be empty. This array is replaced during a strategic merge patch.",
                                                                                        "items": {
                                                                                            "type": "string"
                                                                                        },
                                                                                        "type": "array",
                                                                                    },
                                                                                },
                                                                                "required": [
                                                                                    "key",
                                                                                    "operator",
                                                                                ],
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "matchLabels": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "description": 'matchLabels is a map of {key,value} pairs. A single {key,value} in the matchLabels map is equivalent to an element of matchExpressions, whose key field is "key", the operator is "In", and the values array contains only "value". The requirements are ANDed.',
                                                                            "type": "object",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                    "x-kubernetes-map-type": "atomic",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "secureSettings": {
                                                    "description": "SecureSettings is a list of references to Kubernetes secrets containing sensitive configuration options for Elasticsearch.",
                                                    "items": {
                                                        "description": "SecretSource defines a data source based on a Kubernetes Secret.",
                                                        "properties": {
                                                            "entries": {
                                                                "description": "Entries define how to project each key-value pair in the secret to filesystem paths. If not defined, all keys will be projected to similarly named paths in the filesystem. If defined, only the specified keys will be projected to the corresponding paths.",
                                                                "items": {
                                                                    "description": "KeyToPath defines how to map a key in a Secret object to a filesystem path.",
                                                                    "properties": {
                                                                        "key": {
                                                                            "description": "Key is the key contained in the secret.",
                                                                            "type": "string",
                                                                        },
                                                                        "path": {
                                                                            "description": 'Path is the relative file path to map the key to. Path must not be an absolute file path and must not contain any ".." components.',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "required": ["key"],
                                                                    "type": "object",
                                                                },
                                                                "type": "array",
                                                            },
                                                            "secretName": {
                                                                "description": "SecretName is the name of the secret.",
                                                                "type": "string",
                                                            },
                                                        },
                                                        "required": ["secretName"],
                                                        "type": "object",
                                                    },
                                                    "type": "array",
                                                },
                                                "updateStrategy": {
                                                    "description": "UpdateStrategy specifies how updates to the cluster should be performed.",
                                                    "properties": {
                                                        "changeBudget": {
                                                            "description": "ChangeBudget defines the constraints to consider when applying changes to the Elasticsearch cluster.",
                                                            "properties": {
                                                                "maxSurge": {
                                                                    "description": "MaxSurge is the maximum number of new pods that can be created exceeding the original number of pods defined in the specification. MaxSurge is only taken into consideration when scaling up. Setting a negative value will disable the restriction. Defaults to unbounded if not specified.",
                                                                    "format": "int32",
                                                                    "type": "integer",
                                                                },
                                                                "maxUnavailable": {
                                                                    "description": "MaxUnavailable is the maximum number of pods that can be unavailable (not ready) during the update due to circumstances under the control of the operator. Setting a negative value will disable this restriction. Defaults to 1 if not specified.",
                                                                    "format": "int32",
                                                                    "type": "integer",
                                                                },
                                                            },
                                                            "type": "object",
                                                        }
                                                    },
                                                    "type": "object",
                                                },
                                                "version": {
                                                    "description": "Version of Elasticsearch.",
                                                    "type": "string",
                                                },
                                            },
                                            "required": ["nodeSets"],
                                            "type": "object",
                                        },
                                        "status": {
                                            "description": "ElasticsearchStatus defines the observed state of Elasticsearch",
                                            "properties": {
                                                "availableNodes": {
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "health": {
                                                    "description": "ElasticsearchHealth is the health of the cluster as returned by the health API.",
                                                    "type": "string",
                                                },
                                                "phase": {
                                                    "description": "ElasticsearchOrchestrationPhase is the phase Elasticsearch is in from the controller point of view.",
                                                    "type": "string",
                                                },
                                            },
                                            "type": "object",
                                        },
                                    },
                                    "type": "object",
                                }
                            },
                            "served": True,
                            "storage": False,
                            "subresources": {"status": {}},
                        },
                        {
                            "name": "v1alpha1",
                            "schema": {
                                "openAPIV3Schema": {
                                    "description": "to not break compatibility when upgrading from previous versions of the CRD",
                                    "type": "object",
                                }
                            },
                            "served": False,
                            "storage": False,
                        },
                    ],
                },
            },
            {
                "apiVersion": "apiextensions.k8s.io/v1",
                "kind": "CustomResourceDefinition",
                "metadata": {
                    "annotations": {"controller-gen.kubebuilder.io/version": "v0.10.0"},
                    "creationTimestamp": None,
                    "labels": {
                        "app.kubernetes.io/instance": "elastic-operator",
                        "app.kubernetes.io/name": "eck-operator-crds",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                    "name": "enterprisesearches.enterprisesearch.k8s.elastic.co",
                },
                "spec": {
                    "group": "enterprisesearch.k8s.elastic.co",
                    "names": {
                        "categories": ["elastic"],
                        "kind": "EnterpriseSearch",
                        "listKind": "EnterpriseSearchList",
                        "plural": "enterprisesearches",
                        "shortNames": ["ent"],
                        "singular": "enterprisesearch",
                    },
                    "scope": "Namespaced",
                    "versions": [
                        {
                            "additionalPrinterColumns": [
                                {
                                    "jsonPath": ".status.health",
                                    "name": "health",
                                    "type": "string",
                                },
                                {
                                    "description": "Available nodes",
                                    "jsonPath": ".status.availableNodes",
                                    "name": "nodes",
                                    "type": "integer",
                                },
                                {
                                    "description": "Enterprise Search version",
                                    "jsonPath": ".status.version",
                                    "name": "version",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".metadata.creationTimestamp",
                                    "name": "age",
                                    "type": "date",
                                },
                            ],
                            "name": "v1",
                            "schema": {
                                "openAPIV3Schema": {
                                    "description": "EnterpriseSearch is a Kubernetes CRD to represent Enterprise Search.",
                                    "properties": {
                                        "apiVersion": {
                                            "description": "APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources",
                                            "type": "string",
                                        },
                                        "kind": {
                                            "description": "Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds",
                                            "type": "string",
                                        },
                                        "metadata": {"type": "object"},
                                        "spec": {
                                            "description": "EnterpriseSearchSpec holds the specification of an Enterprise Search resource.",
                                            "properties": {
                                                "config": {
                                                    "description": "Config holds the Enterprise Search configuration.",
                                                    "type": "object",
                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                },
                                                "configRef": {
                                                    "description": "ConfigRef contains a reference to an existing Kubernetes Secret holding the Enterprise Search configuration. Configuration settings are merged and have precedence over settings specified in `config`.",
                                                    "properties": {
                                                        "secretName": {
                                                            "description": "SecretName is the name of the secret.",
                                                            "type": "string",
                                                        }
                                                    },
                                                    "type": "object",
                                                },
                                                "count": {
                                                    "description": "Count of Enterprise Search instances to deploy.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "elasticsearchRef": {
                                                    "description": "ElasticsearchRef is a reference to the Elasticsearch cluster running in the same Kubernetes cluster.",
                                                    "properties": {
                                                        "name": {
                                                            "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                            "type": "string",
                                                        },
                                                        "namespace": {
                                                            "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                            "type": "string",
                                                        },
                                                        "secretName": {
                                                            "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                            "type": "string",
                                                        },
                                                        "serviceName": {
                                                            "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                            "type": "string",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "http": {
                                                    "description": "HTTP holds the HTTP layer configuration for Enterprise Search resource.",
                                                    "properties": {
                                                        "service": {
                                                            "description": "Service defines the template for the associated Kubernetes Service object.",
                                                            "properties": {
                                                                "metadata": {
                                                                    "description": "ObjectMeta is the metadata of the service. The name and namespace provided here are managed by ECK and will be ignored.",
                                                                    "properties": {
                                                                        "annotations": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "finalizers": {
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "labels": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "name": {
                                                                            "type": "string"
                                                                        },
                                                                        "namespace": {
                                                                            "type": "string"
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "spec": {
                                                                    "description": "Spec is the specification of the service.",
                                                                    "properties": {
                                                                        "allocateLoadBalancerNodePorts": {
                                                                            "description": 'allocateLoadBalancerNodePorts defines if NodePorts will be automatically allocated for services with type LoadBalancer.  Default is "true". It may be set to "false" if the cluster load-balancer does not rely on NodePorts.  If the caller requests specific NodePorts (by specifying a value), those requests will be respected, regardless of this field. This field may only be set for services with type LoadBalancer and will be cleared if the type is changed to any other type.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "clusterIP": {
                                                                            "description": 'clusterIP is the IP address of the service and is usually assigned randomly. If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be blank) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address. Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "clusterIPs": {
                                                                            "description": 'ClusterIPs is a list of IP addresses assigned to this service, and are usually assigned randomly.  If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be empty) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address.  Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName.  If this field is not specified, it will be initialized from the clusterIP field.  If this field is specified, clients must ensure that clusterIPs[0] and clusterIP have the same value. \n This field may hold a maximum of two entries (dual-stack IPs, in either order). These IPs must correspond to the values of the ipFamilies field. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "externalIPs": {
                                                                            "description": "externalIPs is a list of IP addresses for which nodes in the cluster will also accept traffic for this service.  These IPs are not managed by Kubernetes.  The user is responsible for ensuring that traffic arrives at a node with this IP.  A common example is external load-balancers that are not part of the Kubernetes system.",
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "externalName": {
                                                                            "description": 'externalName is the external reference that discovery mechanisms will return as an alias for this service (e.g. a DNS CNAME record). No proxying will be involved.  Must be a lowercase RFC-1123 hostname (https://tools.ietf.org/html/rfc1123) and requires `type` to be "ExternalName".',
                                                                            "type": "string",
                                                                        },
                                                                        "externalTrafficPolicy": {
                                                                            "description": 'externalTrafficPolicy describes how nodes distribute service traffic they receive on one of the Service\'s "externally-facing" addresses (NodePorts, ExternalIPs, and LoadBalancer IPs). If set to "Local", the proxy will configure the service in a way that assumes that external load balancers will take care of balancing the service traffic between nodes, and so each node will deliver traffic only to the node-local endpoints of the service, without masquerading the client source IP. (Traffic mistakenly sent to a node with no endpoints will be dropped.) The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features). Note that traffic sent to an External IP or LoadBalancer IP from within the cluster will always get "Cluster" semantics, but clients sending to a NodePort from within the cluster may need to take traffic policy into account when picking a node.',
                                                                            "type": "string",
                                                                        },
                                                                        "healthCheckNodePort": {
                                                                            "description": "healthCheckNodePort specifies the healthcheck nodePort for the service. This only applies when type is set to LoadBalancer and externalTrafficPolicy is set to Local. If a value is specified, is in-range, and is not in use, it will be used.  If not specified, a value will be automatically allocated.  External systems (e.g. load-balancers) can use this port to determine if a given node holds endpoints for this service or not.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type). This field cannot be updated once set.",
                                                                            "format": "int32",
                                                                            "type": "integer",
                                                                        },
                                                                        "internalTrafficPolicy": {
                                                                            "description": 'InternalTrafficPolicy describes how nodes distribute service traffic they receive on the ClusterIP. If set to "Local", the proxy will assume that pods only want to talk to endpoints of the service on the same node as the pod, dropping the traffic if there are no local endpoints. The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features).',
                                                                            "type": "string",
                                                                        },
                                                                        "ipFamilies": {
                                                                            "description": 'IPFamilies is a list of IP families (e.g. IPv4, IPv6) assigned to this service. This field is usually assigned automatically based on cluster configuration and the ipFamilyPolicy field. If this field is specified manually, the requested family is available in the cluster, and ipFamilyPolicy allows it, it will be used; otherwise creation of the service will fail. This field is conditionally mutable: it allows for adding or removing a secondary IP family, but it does not allow changing the primary IP family of the Service. Valid values are "IPv4" and "IPv6".  This field only applies to Services of types ClusterIP, NodePort, and LoadBalancer, and does apply to "headless" services. This field will be wiped when updating a Service to type ExternalName. \n This field may hold a maximum of two entries (dual-stack families, in either order).  These families must correspond to the values of the clusterIPs field, if specified. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field.',
                                                                            "items": {
                                                                                "description": "IPFamily represents the IP Family (IPv4 or IPv6). This type is used to express the family of an IP expressed by a type (e.g. service.spec.ipFamilies).",
                                                                                "type": "string",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "ipFamilyPolicy": {
                                                                            "description": 'IPFamilyPolicy represents the dual-stack-ness requested or required by this Service. If there is no value provided, then this field will be set to SingleStack. Services can be "SingleStack" (a single IP family), "PreferDualStack" (two IP families on dual-stack configured clusters or a single IP family on single-stack clusters), or "RequireDualStack" (two IP families on dual-stack configured clusters, otherwise fail). The ipFamilies and clusterIPs fields depend on the value of this field. This field will be wiped when updating a service to type ExternalName.',
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerClass": {
                                                                            "description": "loadBalancerClass is the class of the load balancer implementation this Service belongs to. If specified, the value of this field must be a label-style identifier, with an optional prefix, e.g. \"internal-vip\" or \"example.com/internal-vip\". Unprefixed names are reserved for end-users. This field can only be set when the Service type is 'LoadBalancer'. If not set, the default load balancer implementation is used, today this is typically done through the cloud provider integration, but should apply for any default implementation. If set, it is assumed that a load balancer implementation is watching for Services with a matching class. Any default load balancer implementation (e.g. cloud providers) should ignore Services that set this field. This field can only be set when creating or updating a Service to type 'LoadBalancer'. Once set, it can not be changed. This field will be wiped when a service is updated to a non 'LoadBalancer' type.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerIP": {
                                                                            "description": "Only applies to Service Type: LoadBalancer. This feature depends on whether the underlying cloud-provider supports specifying the loadBalancerIP when a load balancer is created. This field will be ignored if the cloud-provider does not support the feature. Deprecated: This field was under-specified and its meaning varies across implementations, and it cannot support dual-stack. As of Kubernetes v1.24, users are encouraged to use implementation-specific annotations when available. This field may be removed in a future API version.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerSourceRanges": {
                                                                            "description": 'If specified and supported by the platform, this will restrict traffic through the cloud-provider load-balancer will be restricted to the specified client IPs. This field will be ignored if the cloud-provider does not support the feature." More info: https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "ports": {
                                                                            "description": "The list of ports that are exposed by this service. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies",
                                                                            "items": {
                                                                                "description": "ServicePort contains information on service's port.",
                                                                                "properties": {
                                                                                    "appProtocol": {
                                                                                        "description": "The application protocol for this port. This field follows standard Kubernetes label syntax. Un-prefixed names are reserved for IANA standard service names (as per RFC-6335 and https://www.iana.org/assignments/service-names). Non-standard protocols should use prefixed names such as mycompany.com/my-custom-protocol.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "name": {
                                                                                        "description": "The name of this port within the service. This must be a DNS_LABEL. All ports within a ServiceSpec must have unique names. When considering the endpoints for a Service, this must match the 'name' field in the EndpointPort. Optional if only one ServicePort is defined on this service.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "nodePort": {
                                                                                        "description": "The port on each node on which this service is exposed when type is NodePort or LoadBalancer.  Usually assigned by the system. If a value is specified, in-range, and not in use it will be used, otherwise the operation will fail.  If not specified, a port will be allocated if this Service requires one.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type from NodePort to ClusterIP). More info: https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "port": {
                                                                                        "description": "The port that will be exposed by this service.",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "protocol": {
                                                                                        "default": "TCP",
                                                                                        "description": 'The IP protocol for this port. Supports "TCP", "UDP", and "SCTP". Default is TCP.',
                                                                                        "type": "string",
                                                                                    },
                                                                                    "targetPort": {
                                                                                        "anyOf": [
                                                                                            {
                                                                                                "type": "integer"
                                                                                            },
                                                                                            {
                                                                                                "type": "string"
                                                                                            },
                                                                                        ],
                                                                                        "description": "Number or name of the port to access on the pods targeted by the service. Number must be in the range 1 to 65535. Name must be an IANA_SVC_NAME. If this is a string, it will be looked up as a named port in the target Pod's container ports. If this is not specified, the value of the 'port' field is used (an identity map). This field is ignored for services with clusterIP=None, and should be omitted or set equal to the 'port' field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#defining-a-service",
                                                                                        "x-kubernetes-int-or-string": True,
                                                                                    },
                                                                                },
                                                                                "required": [
                                                                                    "port"
                                                                                ],
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-map-keys": [
                                                                                "port",
                                                                                "protocol",
                                                                            ],
                                                                            "x-kubernetes-list-type": "map",
                                                                        },
                                                                        "publishNotReadyAddresses": {
                                                                            "description": 'publishNotReadyAddresses indicates that any agent which deals with endpoints for this Service should disregard any indications of ready/not-ready. The primary use case for setting this field is for a StatefulSet\'s Headless Service to propagate SRV DNS records for its Pods for the purpose of peer discovery. The Kubernetes controllers that generate Endpoints and EndpointSlice resources for Services interpret this to mean that all endpoints are considered "ready" even if the Pods themselves are not. Agents which consume only Kubernetes generated endpoints through the Endpoints or EndpointSlice resources can safely assume this behavior.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "selector": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "description": "Route service traffic to pods with label keys and values matching this selector. If empty or not present, the service is assumed to have an external process managing its endpoints, which Kubernetes will not modify. Only applies to types ClusterIP, NodePort, and LoadBalancer. Ignored if type is ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/",
                                                                            "type": "object",
                                                                            "x-kubernetes-map-type": "atomic",
                                                                        },
                                                                        "sessionAffinity": {
                                                                            "description": 'Supports "ClientIP" and "None". Used to maintain session affinity. Enable client IP based session affinity. Must be ClientIP or None. Defaults to None. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "sessionAffinityConfig": {
                                                                            "description": "sessionAffinityConfig contains the configurations of session affinity.",
                                                                            "properties": {
                                                                                "clientIP": {
                                                                                    "description": "clientIP contains the configurations of Client IP based session affinity.",
                                                                                    "properties": {
                                                                                        "timeoutSeconds": {
                                                                                            "description": 'timeoutSeconds specifies the seconds of ClientIP type session sticky time. The value must be >0 && <=86400(for 1 day) if ServiceAffinity == "ClientIP". Default value is 10800(for 3 hours).',
                                                                                            "format": "int32",
                                                                                            "type": "integer",
                                                                                        }
                                                                                    },
                                                                                    "type": "object",
                                                                                }
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "type": {
                                                                            "description": 'type determines how the Service is exposed. Defaults to ClusterIP. Valid options are ExternalName, ClusterIP, NodePort, and LoadBalancer. "ClusterIP" allocates a cluster-internal IP address for load-balancing to endpoints. Endpoints are determined by the selector or if that is not specified, by manual construction of an Endpoints object or EndpointSlice objects. If clusterIP is "None", no virtual IP is allocated and the endpoints are published as a set of endpoints rather than a virtual IP. "NodePort" builds on ClusterIP and allocates a port on every node which routes to the same endpoints as the clusterIP. "LoadBalancer" builds on NodePort and creates an external load-balancer (if supported in the current cloud) which routes to the same endpoints as the clusterIP. "ExternalName" aliases this service to the specified externalName. Several other fields do not apply to ExternalName services. More info: https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                        "tls": {
                                                            "description": "TLS defines options for configuring TLS for HTTP.",
                                                            "properties": {
                                                                "certificate": {
                                                                    "description": "Certificate is a reference to a Kubernetes secret that contains the certificate and private key for enabling TLS. The referenced secret should contain the following: \n - `ca.crt`: The certificate authority (optional). - `tls.crt`: The certificate (or a chain). - `tls.key`: The private key to the first certificate in the certificate chain.",
                                                                    "properties": {
                                                                        "secretName": {
                                                                            "description": "SecretName is the name of the secret.",
                                                                            "type": "string",
                                                                        }
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "selfSignedCertificate": {
                                                                    "description": "SelfSignedCertificate allows configuring the self-signed certificate generated by the operator.",
                                                                    "properties": {
                                                                        "disabled": {
                                                                            "description": "Disabled indicates that the provisioning of the self-signed certifcate should be disabled.",
                                                                            "type": "boolean",
                                                                        },
                                                                        "subjectAltNames": {
                                                                            "description": "SubjectAlternativeNames is a list of SANs to include in the generated HTTP TLS certificate.",
                                                                            "items": {
                                                                                "description": "SubjectAlternativeName represents a SAN entry in a x509 certificate.",
                                                                                "properties": {
                                                                                    "dns": {
                                                                                        "description": "DNS is the DNS name of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "ip": {
                                                                                        "description": "IP is the IP address of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                },
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "image": {
                                                    "description": "Image is the Enterprise Search Docker image to deploy.",
                                                    "type": "string",
                                                },
                                                "podTemplate": {
                                                    "description": "PodTemplate provides customisation options (labels, annotations, affinity rules, resource requests, and so on) for the Enterprise Search pods.",
                                                    "type": "object",
                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                },
                                                "revisionHistoryLimit": {
                                                    "description": "RevisionHistoryLimit is the number of revisions to retain to allow rollback in the underlying Deployment.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "serviceAccountName": {
                                                    "description": "ServiceAccountName is used to check access from the current resource to a resource (for ex. Elasticsearch) in a different namespace. Can only be used if ECK is enforcing RBAC on references.",
                                                    "type": "string",
                                                },
                                                "version": {
                                                    "description": "Version of Enterprise Search.",
                                                    "type": "string",
                                                },
                                            },
                                            "type": "object",
                                        },
                                        "status": {
                                            "description": "EnterpriseSearchStatus defines the observed state of EnterpriseSearch",
                                            "properties": {
                                                "associationStatus": {
                                                    "description": "Association is the status of any auto-linking to Elasticsearch clusters.",
                                                    "type": "string",
                                                },
                                                "availableNodes": {
                                                    "description": "AvailableNodes is the number of available replicas in the deployment.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "count": {
                                                    "description": "Count corresponds to Scale.Status.Replicas, which is the actual number of observed instances of the scaled object.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "health": {
                                                    "description": "Health of the deployment.",
                                                    "type": "string",
                                                },
                                                "observedGeneration": {
                                                    "description": "ObservedGeneration represents the .metadata.generation that the status is based upon. It corresponds to the metadata generation, which is updated on mutation by the API Server. If the generation observed in status diverges from the generation in metadata, the Enterprise Search controller has not yet processed the changes contained in the Enterprise Search specification.",
                                                    "format": "int64",
                                                    "type": "integer",
                                                },
                                                "selector": {
                                                    "description": "Selector is the label selector used to find all pods.",
                                                    "type": "string",
                                                },
                                                "service": {
                                                    "description": "ExternalService is the name of the service associated to the Enterprise Search Pods.",
                                                    "type": "string",
                                                },
                                                "version": {
                                                    "description": "Version of the stack resource currently running. During version upgrades, multiple versions may run in parallel: this value specifies the lowest version currently running.",
                                                    "type": "string",
                                                },
                                            },
                                            "type": "object",
                                        },
                                    },
                                    "type": "object",
                                }
                            },
                            "served": True,
                            "storage": True,
                            "subresources": {
                                "scale": {
                                    "labelSelectorPath": ".status.selector",
                                    "specReplicasPath": ".spec.count",
                                    "statusReplicasPath": ".status.count",
                                },
                                "status": {},
                            },
                        },
                        {
                            "additionalPrinterColumns": [
                                {
                                    "jsonPath": ".status.health",
                                    "name": "health",
                                    "type": "string",
                                },
                                {
                                    "description": "Available nodes",
                                    "jsonPath": ".status.availableNodes",
                                    "name": "nodes",
                                    "type": "integer",
                                },
                                {
                                    "description": "Enterprise Search version",
                                    "jsonPath": ".status.version",
                                    "name": "version",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".metadata.creationTimestamp",
                                    "name": "age",
                                    "type": "date",
                                },
                            ],
                            "name": "v1beta1",
                            "schema": {
                                "openAPIV3Schema": {
                                    "description": "EnterpriseSearch is a Kubernetes CRD to represent Enterprise Search.",
                                    "properties": {
                                        "apiVersion": {
                                            "description": "APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources",
                                            "type": "string",
                                        },
                                        "kind": {
                                            "description": "Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds",
                                            "type": "string",
                                        },
                                        "metadata": {"type": "object"},
                                        "spec": {
                                            "description": "EnterpriseSearchSpec holds the specification of an Enterprise Search resource.",
                                            "properties": {
                                                "config": {
                                                    "description": "Config holds the Enterprise Search configuration.",
                                                    "type": "object",
                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                },
                                                "configRef": {
                                                    "description": "ConfigRef contains a reference to an existing Kubernetes Secret holding the Enterprise Search configuration. Configuration settings are merged and have precedence over settings specified in `config`.",
                                                    "properties": {
                                                        "secretName": {
                                                            "description": "SecretName is the name of the secret.",
                                                            "type": "string",
                                                        }
                                                    },
                                                    "type": "object",
                                                },
                                                "count": {
                                                    "description": "Count of Enterprise Search instances to deploy.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "elasticsearchRef": {
                                                    "description": "ElasticsearchRef is a reference to the Elasticsearch cluster running in the same Kubernetes cluster.",
                                                    "properties": {
                                                        "name": {
                                                            "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                            "type": "string",
                                                        },
                                                        "namespace": {
                                                            "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                            "type": "string",
                                                        },
                                                        "secretName": {
                                                            "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                            "type": "string",
                                                        },
                                                        "serviceName": {
                                                            "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                            "type": "string",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "http": {
                                                    "description": "HTTP holds the HTTP layer configuration for Enterprise Search resource.",
                                                    "properties": {
                                                        "service": {
                                                            "description": "Service defines the template for the associated Kubernetes Service object.",
                                                            "properties": {
                                                                "metadata": {
                                                                    "description": "ObjectMeta is the metadata of the service. The name and namespace provided here are managed by ECK and will be ignored.",
                                                                    "properties": {
                                                                        "annotations": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "finalizers": {
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "labels": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "name": {
                                                                            "type": "string"
                                                                        },
                                                                        "namespace": {
                                                                            "type": "string"
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "spec": {
                                                                    "description": "Spec is the specification of the service.",
                                                                    "properties": {
                                                                        "allocateLoadBalancerNodePorts": {
                                                                            "description": 'allocateLoadBalancerNodePorts defines if NodePorts will be automatically allocated for services with type LoadBalancer.  Default is "true". It may be set to "false" if the cluster load-balancer does not rely on NodePorts.  If the caller requests specific NodePorts (by specifying a value), those requests will be respected, regardless of this field. This field may only be set for services with type LoadBalancer and will be cleared if the type is changed to any other type.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "clusterIP": {
                                                                            "description": 'clusterIP is the IP address of the service and is usually assigned randomly. If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be blank) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address. Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "clusterIPs": {
                                                                            "description": 'ClusterIPs is a list of IP addresses assigned to this service, and are usually assigned randomly.  If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be empty) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address.  Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName.  If this field is not specified, it will be initialized from the clusterIP field.  If this field is specified, clients must ensure that clusterIPs[0] and clusterIP have the same value. \n This field may hold a maximum of two entries (dual-stack IPs, in either order). These IPs must correspond to the values of the ipFamilies field. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "externalIPs": {
                                                                            "description": "externalIPs is a list of IP addresses for which nodes in the cluster will also accept traffic for this service.  These IPs are not managed by Kubernetes.  The user is responsible for ensuring that traffic arrives at a node with this IP.  A common example is external load-balancers that are not part of the Kubernetes system.",
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "externalName": {
                                                                            "description": 'externalName is the external reference that discovery mechanisms will return as an alias for this service (e.g. a DNS CNAME record). No proxying will be involved.  Must be a lowercase RFC-1123 hostname (https://tools.ietf.org/html/rfc1123) and requires `type` to be "ExternalName".',
                                                                            "type": "string",
                                                                        },
                                                                        "externalTrafficPolicy": {
                                                                            "description": 'externalTrafficPolicy describes how nodes distribute service traffic they receive on one of the Service\'s "externally-facing" addresses (NodePorts, ExternalIPs, and LoadBalancer IPs). If set to "Local", the proxy will configure the service in a way that assumes that external load balancers will take care of balancing the service traffic between nodes, and so each node will deliver traffic only to the node-local endpoints of the service, without masquerading the client source IP. (Traffic mistakenly sent to a node with no endpoints will be dropped.) The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features). Note that traffic sent to an External IP or LoadBalancer IP from within the cluster will always get "Cluster" semantics, but clients sending to a NodePort from within the cluster may need to take traffic policy into account when picking a node.',
                                                                            "type": "string",
                                                                        },
                                                                        "healthCheckNodePort": {
                                                                            "description": "healthCheckNodePort specifies the healthcheck nodePort for the service. This only applies when type is set to LoadBalancer and externalTrafficPolicy is set to Local. If a value is specified, is in-range, and is not in use, it will be used.  If not specified, a value will be automatically allocated.  External systems (e.g. load-balancers) can use this port to determine if a given node holds endpoints for this service or not.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type). This field cannot be updated once set.",
                                                                            "format": "int32",
                                                                            "type": "integer",
                                                                        },
                                                                        "internalTrafficPolicy": {
                                                                            "description": 'InternalTrafficPolicy describes how nodes distribute service traffic they receive on the ClusterIP. If set to "Local", the proxy will assume that pods only want to talk to endpoints of the service on the same node as the pod, dropping the traffic if there are no local endpoints. The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features).',
                                                                            "type": "string",
                                                                        },
                                                                        "ipFamilies": {
                                                                            "description": 'IPFamilies is a list of IP families (e.g. IPv4, IPv6) assigned to this service. This field is usually assigned automatically based on cluster configuration and the ipFamilyPolicy field. If this field is specified manually, the requested family is available in the cluster, and ipFamilyPolicy allows it, it will be used; otherwise creation of the service will fail. This field is conditionally mutable: it allows for adding or removing a secondary IP family, but it does not allow changing the primary IP family of the Service. Valid values are "IPv4" and "IPv6".  This field only applies to Services of types ClusterIP, NodePort, and LoadBalancer, and does apply to "headless" services. This field will be wiped when updating a Service to type ExternalName. \n This field may hold a maximum of two entries (dual-stack families, in either order).  These families must correspond to the values of the clusterIPs field, if specified. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field.',
                                                                            "items": {
                                                                                "description": "IPFamily represents the IP Family (IPv4 or IPv6). This type is used to express the family of an IP expressed by a type (e.g. service.spec.ipFamilies).",
                                                                                "type": "string",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "ipFamilyPolicy": {
                                                                            "description": 'IPFamilyPolicy represents the dual-stack-ness requested or required by this Service. If there is no value provided, then this field will be set to SingleStack. Services can be "SingleStack" (a single IP family), "PreferDualStack" (two IP families on dual-stack configured clusters or a single IP family on single-stack clusters), or "RequireDualStack" (two IP families on dual-stack configured clusters, otherwise fail). The ipFamilies and clusterIPs fields depend on the value of this field. This field will be wiped when updating a service to type ExternalName.',
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerClass": {
                                                                            "description": "loadBalancerClass is the class of the load balancer implementation this Service belongs to. If specified, the value of this field must be a label-style identifier, with an optional prefix, e.g. \"internal-vip\" or \"example.com/internal-vip\". Unprefixed names are reserved for end-users. This field can only be set when the Service type is 'LoadBalancer'. If not set, the default load balancer implementation is used, today this is typically done through the cloud provider integration, but should apply for any default implementation. If set, it is assumed that a load balancer implementation is watching for Services with a matching class. Any default load balancer implementation (e.g. cloud providers) should ignore Services that set this field. This field can only be set when creating or updating a Service to type 'LoadBalancer'. Once set, it can not be changed. This field will be wiped when a service is updated to a non 'LoadBalancer' type.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerIP": {
                                                                            "description": "Only applies to Service Type: LoadBalancer. This feature depends on whether the underlying cloud-provider supports specifying the loadBalancerIP when a load balancer is created. This field will be ignored if the cloud-provider does not support the feature. Deprecated: This field was under-specified and its meaning varies across implementations, and it cannot support dual-stack. As of Kubernetes v1.24, users are encouraged to use implementation-specific annotations when available. This field may be removed in a future API version.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerSourceRanges": {
                                                                            "description": 'If specified and supported by the platform, this will restrict traffic through the cloud-provider load-balancer will be restricted to the specified client IPs. This field will be ignored if the cloud-provider does not support the feature." More info: https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "ports": {
                                                                            "description": "The list of ports that are exposed by this service. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies",
                                                                            "items": {
                                                                                "description": "ServicePort contains information on service's port.",
                                                                                "properties": {
                                                                                    "appProtocol": {
                                                                                        "description": "The application protocol for this port. This field follows standard Kubernetes label syntax. Un-prefixed names are reserved for IANA standard service names (as per RFC-6335 and https://www.iana.org/assignments/service-names). Non-standard protocols should use prefixed names such as mycompany.com/my-custom-protocol.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "name": {
                                                                                        "description": "The name of this port within the service. This must be a DNS_LABEL. All ports within a ServiceSpec must have unique names. When considering the endpoints for a Service, this must match the 'name' field in the EndpointPort. Optional if only one ServicePort is defined on this service.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "nodePort": {
                                                                                        "description": "The port on each node on which this service is exposed when type is NodePort or LoadBalancer.  Usually assigned by the system. If a value is specified, in-range, and not in use it will be used, otherwise the operation will fail.  If not specified, a port will be allocated if this Service requires one.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type from NodePort to ClusterIP). More info: https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "port": {
                                                                                        "description": "The port that will be exposed by this service.",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "protocol": {
                                                                                        "default": "TCP",
                                                                                        "description": 'The IP protocol for this port. Supports "TCP", "UDP", and "SCTP". Default is TCP.',
                                                                                        "type": "string",
                                                                                    },
                                                                                    "targetPort": {
                                                                                        "anyOf": [
                                                                                            {
                                                                                                "type": "integer"
                                                                                            },
                                                                                            {
                                                                                                "type": "string"
                                                                                            },
                                                                                        ],
                                                                                        "description": "Number or name of the port to access on the pods targeted by the service. Number must be in the range 1 to 65535. Name must be an IANA_SVC_NAME. If this is a string, it will be looked up as a named port in the target Pod's container ports. If this is not specified, the value of the 'port' field is used (an identity map). This field is ignored for services with clusterIP=None, and should be omitted or set equal to the 'port' field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#defining-a-service",
                                                                                        "x-kubernetes-int-or-string": True,
                                                                                    },
                                                                                },
                                                                                "required": [
                                                                                    "port"
                                                                                ],
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-map-keys": [
                                                                                "port",
                                                                                "protocol",
                                                                            ],
                                                                            "x-kubernetes-list-type": "map",
                                                                        },
                                                                        "publishNotReadyAddresses": {
                                                                            "description": 'publishNotReadyAddresses indicates that any agent which deals with endpoints for this Service should disregard any indications of ready/not-ready. The primary use case for setting this field is for a StatefulSet\'s Headless Service to propagate SRV DNS records for its Pods for the purpose of peer discovery. The Kubernetes controllers that generate Endpoints and EndpointSlice resources for Services interpret this to mean that all endpoints are considered "ready" even if the Pods themselves are not. Agents which consume only Kubernetes generated endpoints through the Endpoints or EndpointSlice resources can safely assume this behavior.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "selector": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "description": "Route service traffic to pods with label keys and values matching this selector. If empty or not present, the service is assumed to have an external process managing its endpoints, which Kubernetes will not modify. Only applies to types ClusterIP, NodePort, and LoadBalancer. Ignored if type is ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/",
                                                                            "type": "object",
                                                                            "x-kubernetes-map-type": "atomic",
                                                                        },
                                                                        "sessionAffinity": {
                                                                            "description": 'Supports "ClientIP" and "None". Used to maintain session affinity. Enable client IP based session affinity. Must be ClientIP or None. Defaults to None. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "sessionAffinityConfig": {
                                                                            "description": "sessionAffinityConfig contains the configurations of session affinity.",
                                                                            "properties": {
                                                                                "clientIP": {
                                                                                    "description": "clientIP contains the configurations of Client IP based session affinity.",
                                                                                    "properties": {
                                                                                        "timeoutSeconds": {
                                                                                            "description": 'timeoutSeconds specifies the seconds of ClientIP type session sticky time. The value must be >0 && <=86400(for 1 day) if ServiceAffinity == "ClientIP". Default value is 10800(for 3 hours).',
                                                                                            "format": "int32",
                                                                                            "type": "integer",
                                                                                        }
                                                                                    },
                                                                                    "type": "object",
                                                                                }
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "type": {
                                                                            "description": 'type determines how the Service is exposed. Defaults to ClusterIP. Valid options are ExternalName, ClusterIP, NodePort, and LoadBalancer. "ClusterIP" allocates a cluster-internal IP address for load-balancing to endpoints. Endpoints are determined by the selector or if that is not specified, by manual construction of an Endpoints object or EndpointSlice objects. If clusterIP is "None", no virtual IP is allocated and the endpoints are published as a set of endpoints rather than a virtual IP. "NodePort" builds on ClusterIP and allocates a port on every node which routes to the same endpoints as the clusterIP. "LoadBalancer" builds on NodePort and creates an external load-balancer (if supported in the current cloud) which routes to the same endpoints as the clusterIP. "ExternalName" aliases this service to the specified externalName. Several other fields do not apply to ExternalName services. More info: https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                        "tls": {
                                                            "description": "TLS defines options for configuring TLS for HTTP.",
                                                            "properties": {
                                                                "certificate": {
                                                                    "description": "Certificate is a reference to a Kubernetes secret that contains the certificate and private key for enabling TLS. The referenced secret should contain the following: \n - `ca.crt`: The certificate authority (optional). - `tls.crt`: The certificate (or a chain). - `tls.key`: The private key to the first certificate in the certificate chain.",
                                                                    "properties": {
                                                                        "secretName": {
                                                                            "description": "SecretName is the name of the secret.",
                                                                            "type": "string",
                                                                        }
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "selfSignedCertificate": {
                                                                    "description": "SelfSignedCertificate allows configuring the self-signed certificate generated by the operator.",
                                                                    "properties": {
                                                                        "disabled": {
                                                                            "description": "Disabled indicates that the provisioning of the self-signed certifcate should be disabled.",
                                                                            "type": "boolean",
                                                                        },
                                                                        "subjectAltNames": {
                                                                            "description": "SubjectAlternativeNames is a list of SANs to include in the generated HTTP TLS certificate.",
                                                                            "items": {
                                                                                "description": "SubjectAlternativeName represents a SAN entry in a x509 certificate.",
                                                                                "properties": {
                                                                                    "dns": {
                                                                                        "description": "DNS is the DNS name of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "ip": {
                                                                                        "description": "IP is the IP address of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                },
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "image": {
                                                    "description": "Image is the Enterprise Search Docker image to deploy.",
                                                    "type": "string",
                                                },
                                                "podTemplate": {
                                                    "description": "PodTemplate provides customisation options (labels, annotations, affinity rules, resource requests, and so on) for the Enterprise Search pods.",
                                                    "type": "object",
                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                },
                                                "serviceAccountName": {
                                                    "description": "ServiceAccountName is used to check access from the current resource to a resource (for ex. Elasticsearch) in a different namespace. Can only be used if ECK is enforcing RBAC on references.",
                                                    "type": "string",
                                                },
                                                "version": {
                                                    "description": "Version of Enterprise Search.",
                                                    "type": "string",
                                                },
                                            },
                                            "type": "object",
                                        },
                                        "status": {
                                            "description": "EnterpriseSearchStatus defines the observed state of EnterpriseSearch",
                                            "properties": {
                                                "associationStatus": {
                                                    "description": "Association is the status of any auto-linking to Elasticsearch clusters.",
                                                    "type": "string",
                                                },
                                                "availableNodes": {
                                                    "description": "AvailableNodes is the number of available replicas in the deployment.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "count": {
                                                    "description": "Count corresponds to Scale.Status.Replicas, which is the actual number of observed instances of the scaled object.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "health": {
                                                    "description": "Health of the deployment.",
                                                    "type": "string",
                                                },
                                                "selector": {
                                                    "description": "Selector is the label selector used to find all pods.",
                                                    "type": "string",
                                                },
                                                "service": {
                                                    "description": "ExternalService is the name of the service associated to the Enterprise Search Pods.",
                                                    "type": "string",
                                                },
                                                "version": {
                                                    "description": "Version of the stack resource currently running. During version upgrades, multiple versions may run in parallel: this value specifies the lowest version currently running.",
                                                    "type": "string",
                                                },
                                            },
                                            "type": "object",
                                        },
                                    },
                                    "type": "object",
                                }
                            },
                            "served": True,
                            "storage": False,
                            "subresources": {"status": {}},
                        },
                    ],
                },
            },
            {
                "apiVersion": "apiextensions.k8s.io/v1",
                "kind": "CustomResourceDefinition",
                "metadata": {
                    "annotations": {"controller-gen.kubebuilder.io/version": "v0.10.0"},
                    "creationTimestamp": None,
                    "labels": {
                        "app.kubernetes.io/instance": "elastic-operator",
                        "app.kubernetes.io/name": "eck-operator-crds",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                    "name": "kibanas.kibana.k8s.elastic.co",
                },
                "spec": {
                    "group": "kibana.k8s.elastic.co",
                    "names": {
                        "categories": ["elastic"],
                        "kind": "Kibana",
                        "listKind": "KibanaList",
                        "plural": "kibanas",
                        "shortNames": ["kb"],
                        "singular": "kibana",
                    },
                    "scope": "Namespaced",
                    "versions": [
                        {
                            "additionalPrinterColumns": [
                                {
                                    "jsonPath": ".status.health",
                                    "name": "health",
                                    "type": "string",
                                },
                                {
                                    "description": "Available nodes",
                                    "jsonPath": ".status.availableNodes",
                                    "name": "nodes",
                                    "type": "integer",
                                },
                                {
                                    "description": "Kibana version",
                                    "jsonPath": ".status.version",
                                    "name": "version",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".metadata.creationTimestamp",
                                    "name": "age",
                                    "type": "date",
                                },
                            ],
                            "name": "v1",
                            "schema": {
                                "openAPIV3Schema": {
                                    "description": "Kibana represents a Kibana resource in a Kubernetes cluster.",
                                    "properties": {
                                        "apiVersion": {
                                            "description": "APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources",
                                            "type": "string",
                                        },
                                        "kind": {
                                            "description": "Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds",
                                            "type": "string",
                                        },
                                        "metadata": {"type": "object"},
                                        "spec": {
                                            "description": "KibanaSpec holds the specification of a Kibana instance.",
                                            "properties": {
                                                "config": {
                                                    "description": "Config holds the Kibana configuration. See: https://www.elastic.co/guide/en/kibana/current/settings.html",
                                                    "type": "object",
                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                },
                                                "count": {
                                                    "description": "Count of Kibana instances to deploy.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "elasticsearchRef": {
                                                    "description": "ElasticsearchRef is a reference to an Elasticsearch cluster running in the same Kubernetes cluster.",
                                                    "properties": {
                                                        "name": {
                                                            "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                            "type": "string",
                                                        },
                                                        "namespace": {
                                                            "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                            "type": "string",
                                                        },
                                                        "secretName": {
                                                            "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                            "type": "string",
                                                        },
                                                        "serviceName": {
                                                            "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                            "type": "string",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "enterpriseSearchRef": {
                                                    "description": "EnterpriseSearchRef is a reference to an EnterpriseSearch running in the same Kubernetes cluster. Kibana provides the default Enterprise Search UI starting version 7.14.",
                                                    "properties": {
                                                        "name": {
                                                            "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                            "type": "string",
                                                        },
                                                        "namespace": {
                                                            "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                            "type": "string",
                                                        },
                                                        "secretName": {
                                                            "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                            "type": "string",
                                                        },
                                                        "serviceName": {
                                                            "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                            "type": "string",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "http": {
                                                    "description": "HTTP holds the HTTP layer configuration for Kibana.",
                                                    "properties": {
                                                        "service": {
                                                            "description": "Service defines the template for the associated Kubernetes Service object.",
                                                            "properties": {
                                                                "metadata": {
                                                                    "description": "ObjectMeta is the metadata of the service. The name and namespace provided here are managed by ECK and will be ignored.",
                                                                    "properties": {
                                                                        "annotations": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "finalizers": {
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "labels": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "name": {
                                                                            "type": "string"
                                                                        },
                                                                        "namespace": {
                                                                            "type": "string"
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "spec": {
                                                                    "description": "Spec is the specification of the service.",
                                                                    "properties": {
                                                                        "allocateLoadBalancerNodePorts": {
                                                                            "description": 'allocateLoadBalancerNodePorts defines if NodePorts will be automatically allocated for services with type LoadBalancer.  Default is "true". It may be set to "false" if the cluster load-balancer does not rely on NodePorts.  If the caller requests specific NodePorts (by specifying a value), those requests will be respected, regardless of this field. This field may only be set for services with type LoadBalancer and will be cleared if the type is changed to any other type.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "clusterIP": {
                                                                            "description": 'clusterIP is the IP address of the service and is usually assigned randomly. If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be blank) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address. Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "clusterIPs": {
                                                                            "description": 'ClusterIPs is a list of IP addresses assigned to this service, and are usually assigned randomly.  If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be empty) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address.  Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName.  If this field is not specified, it will be initialized from the clusterIP field.  If this field is specified, clients must ensure that clusterIPs[0] and clusterIP have the same value. \n This field may hold a maximum of two entries (dual-stack IPs, in either order). These IPs must correspond to the values of the ipFamilies field. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "externalIPs": {
                                                                            "description": "externalIPs is a list of IP addresses for which nodes in the cluster will also accept traffic for this service.  These IPs are not managed by Kubernetes.  The user is responsible for ensuring that traffic arrives at a node with this IP.  A common example is external load-balancers that are not part of the Kubernetes system.",
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "externalName": {
                                                                            "description": 'externalName is the external reference that discovery mechanisms will return as an alias for this service (e.g. a DNS CNAME record). No proxying will be involved.  Must be a lowercase RFC-1123 hostname (https://tools.ietf.org/html/rfc1123) and requires `type` to be "ExternalName".',
                                                                            "type": "string",
                                                                        },
                                                                        "externalTrafficPolicy": {
                                                                            "description": 'externalTrafficPolicy describes how nodes distribute service traffic they receive on one of the Service\'s "externally-facing" addresses (NodePorts, ExternalIPs, and LoadBalancer IPs). If set to "Local", the proxy will configure the service in a way that assumes that external load balancers will take care of balancing the service traffic between nodes, and so each node will deliver traffic only to the node-local endpoints of the service, without masquerading the client source IP. (Traffic mistakenly sent to a node with no endpoints will be dropped.) The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features). Note that traffic sent to an External IP or LoadBalancer IP from within the cluster will always get "Cluster" semantics, but clients sending to a NodePort from within the cluster may need to take traffic policy into account when picking a node.',
                                                                            "type": "string",
                                                                        },
                                                                        "healthCheckNodePort": {
                                                                            "description": "healthCheckNodePort specifies the healthcheck nodePort for the service. This only applies when type is set to LoadBalancer and externalTrafficPolicy is set to Local. If a value is specified, is in-range, and is not in use, it will be used.  If not specified, a value will be automatically allocated.  External systems (e.g. load-balancers) can use this port to determine if a given node holds endpoints for this service or not.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type). This field cannot be updated once set.",
                                                                            "format": "int32",
                                                                            "type": "integer",
                                                                        },
                                                                        "internalTrafficPolicy": {
                                                                            "description": 'InternalTrafficPolicy describes how nodes distribute service traffic they receive on the ClusterIP. If set to "Local", the proxy will assume that pods only want to talk to endpoints of the service on the same node as the pod, dropping the traffic if there are no local endpoints. The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features).',
                                                                            "type": "string",
                                                                        },
                                                                        "ipFamilies": {
                                                                            "description": 'IPFamilies is a list of IP families (e.g. IPv4, IPv6) assigned to this service. This field is usually assigned automatically based on cluster configuration and the ipFamilyPolicy field. If this field is specified manually, the requested family is available in the cluster, and ipFamilyPolicy allows it, it will be used; otherwise creation of the service will fail. This field is conditionally mutable: it allows for adding or removing a secondary IP family, but it does not allow changing the primary IP family of the Service. Valid values are "IPv4" and "IPv6".  This field only applies to Services of types ClusterIP, NodePort, and LoadBalancer, and does apply to "headless" services. This field will be wiped when updating a Service to type ExternalName. \n This field may hold a maximum of two entries (dual-stack families, in either order).  These families must correspond to the values of the clusterIPs field, if specified. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field.',
                                                                            "items": {
                                                                                "description": "IPFamily represents the IP Family (IPv4 or IPv6). This type is used to express the family of an IP expressed by a type (e.g. service.spec.ipFamilies).",
                                                                                "type": "string",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "ipFamilyPolicy": {
                                                                            "description": 'IPFamilyPolicy represents the dual-stack-ness requested or required by this Service. If there is no value provided, then this field will be set to SingleStack. Services can be "SingleStack" (a single IP family), "PreferDualStack" (two IP families on dual-stack configured clusters or a single IP family on single-stack clusters), or "RequireDualStack" (two IP families on dual-stack configured clusters, otherwise fail). The ipFamilies and clusterIPs fields depend on the value of this field. This field will be wiped when updating a service to type ExternalName.',
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerClass": {
                                                                            "description": "loadBalancerClass is the class of the load balancer implementation this Service belongs to. If specified, the value of this field must be a label-style identifier, with an optional prefix, e.g. \"internal-vip\" or \"example.com/internal-vip\". Unprefixed names are reserved for end-users. This field can only be set when the Service type is 'LoadBalancer'. If not set, the default load balancer implementation is used, today this is typically done through the cloud provider integration, but should apply for any default implementation. If set, it is assumed that a load balancer implementation is watching for Services with a matching class. Any default load balancer implementation (e.g. cloud providers) should ignore Services that set this field. This field can only be set when creating or updating a Service to type 'LoadBalancer'. Once set, it can not be changed. This field will be wiped when a service is updated to a non 'LoadBalancer' type.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerIP": {
                                                                            "description": "Only applies to Service Type: LoadBalancer. This feature depends on whether the underlying cloud-provider supports specifying the loadBalancerIP when a load balancer is created. This field will be ignored if the cloud-provider does not support the feature. Deprecated: This field was under-specified and its meaning varies across implementations, and it cannot support dual-stack. As of Kubernetes v1.24, users are encouraged to use implementation-specific annotations when available. This field may be removed in a future API version.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerSourceRanges": {
                                                                            "description": 'If specified and supported by the platform, this will restrict traffic through the cloud-provider load-balancer will be restricted to the specified client IPs. This field will be ignored if the cloud-provider does not support the feature." More info: https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "ports": {
                                                                            "description": "The list of ports that are exposed by this service. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies",
                                                                            "items": {
                                                                                "description": "ServicePort contains information on service's port.",
                                                                                "properties": {
                                                                                    "appProtocol": {
                                                                                        "description": "The application protocol for this port. This field follows standard Kubernetes label syntax. Un-prefixed names are reserved for IANA standard service names (as per RFC-6335 and https://www.iana.org/assignments/service-names). Non-standard protocols should use prefixed names such as mycompany.com/my-custom-protocol.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "name": {
                                                                                        "description": "The name of this port within the service. This must be a DNS_LABEL. All ports within a ServiceSpec must have unique names. When considering the endpoints for a Service, this must match the 'name' field in the EndpointPort. Optional if only one ServicePort is defined on this service.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "nodePort": {
                                                                                        "description": "The port on each node on which this service is exposed when type is NodePort or LoadBalancer.  Usually assigned by the system. If a value is specified, in-range, and not in use it will be used, otherwise the operation will fail.  If not specified, a port will be allocated if this Service requires one.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type from NodePort to ClusterIP). More info: https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "port": {
                                                                                        "description": "The port that will be exposed by this service.",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "protocol": {
                                                                                        "default": "TCP",
                                                                                        "description": 'The IP protocol for this port. Supports "TCP", "UDP", and "SCTP". Default is TCP.',
                                                                                        "type": "string",
                                                                                    },
                                                                                    "targetPort": {
                                                                                        "anyOf": [
                                                                                            {
                                                                                                "type": "integer"
                                                                                            },
                                                                                            {
                                                                                                "type": "string"
                                                                                            },
                                                                                        ],
                                                                                        "description": "Number or name of the port to access on the pods targeted by the service. Number must be in the range 1 to 65535. Name must be an IANA_SVC_NAME. If this is a string, it will be looked up as a named port in the target Pod's container ports. If this is not specified, the value of the 'port' field is used (an identity map). This field is ignored for services with clusterIP=None, and should be omitted or set equal to the 'port' field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#defining-a-service",
                                                                                        "x-kubernetes-int-or-string": True,
                                                                                    },
                                                                                },
                                                                                "required": [
                                                                                    "port"
                                                                                ],
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-map-keys": [
                                                                                "port",
                                                                                "protocol",
                                                                            ],
                                                                            "x-kubernetes-list-type": "map",
                                                                        },
                                                                        "publishNotReadyAddresses": {
                                                                            "description": 'publishNotReadyAddresses indicates that any agent which deals with endpoints for this Service should disregard any indications of ready/not-ready. The primary use case for setting this field is for a StatefulSet\'s Headless Service to propagate SRV DNS records for its Pods for the purpose of peer discovery. The Kubernetes controllers that generate Endpoints and EndpointSlice resources for Services interpret this to mean that all endpoints are considered "ready" even if the Pods themselves are not. Agents which consume only Kubernetes generated endpoints through the Endpoints or EndpointSlice resources can safely assume this behavior.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "selector": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "description": "Route service traffic to pods with label keys and values matching this selector. If empty or not present, the service is assumed to have an external process managing its endpoints, which Kubernetes will not modify. Only applies to types ClusterIP, NodePort, and LoadBalancer. Ignored if type is ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/",
                                                                            "type": "object",
                                                                            "x-kubernetes-map-type": "atomic",
                                                                        },
                                                                        "sessionAffinity": {
                                                                            "description": 'Supports "ClientIP" and "None". Used to maintain session affinity. Enable client IP based session affinity. Must be ClientIP or None. Defaults to None. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "sessionAffinityConfig": {
                                                                            "description": "sessionAffinityConfig contains the configurations of session affinity.",
                                                                            "properties": {
                                                                                "clientIP": {
                                                                                    "description": "clientIP contains the configurations of Client IP based session affinity.",
                                                                                    "properties": {
                                                                                        "timeoutSeconds": {
                                                                                            "description": 'timeoutSeconds specifies the seconds of ClientIP type session sticky time. The value must be >0 && <=86400(for 1 day) if ServiceAffinity == "ClientIP". Default value is 10800(for 3 hours).',
                                                                                            "format": "int32",
                                                                                            "type": "integer",
                                                                                        }
                                                                                    },
                                                                                    "type": "object",
                                                                                }
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "type": {
                                                                            "description": 'type determines how the Service is exposed. Defaults to ClusterIP. Valid options are ExternalName, ClusterIP, NodePort, and LoadBalancer. "ClusterIP" allocates a cluster-internal IP address for load-balancing to endpoints. Endpoints are determined by the selector or if that is not specified, by manual construction of an Endpoints object or EndpointSlice objects. If clusterIP is "None", no virtual IP is allocated and the endpoints are published as a set of endpoints rather than a virtual IP. "NodePort" builds on ClusterIP and allocates a port on every node which routes to the same endpoints as the clusterIP. "LoadBalancer" builds on NodePort and creates an external load-balancer (if supported in the current cloud) which routes to the same endpoints as the clusterIP. "ExternalName" aliases this service to the specified externalName. Several other fields do not apply to ExternalName services. More info: https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                        "tls": {
                                                            "description": "TLS defines options for configuring TLS for HTTP.",
                                                            "properties": {
                                                                "certificate": {
                                                                    "description": "Certificate is a reference to a Kubernetes secret that contains the certificate and private key for enabling TLS. The referenced secret should contain the following: \n - `ca.crt`: The certificate authority (optional). - `tls.crt`: The certificate (or a chain). - `tls.key`: The private key to the first certificate in the certificate chain.",
                                                                    "properties": {
                                                                        "secretName": {
                                                                            "description": "SecretName is the name of the secret.",
                                                                            "type": "string",
                                                                        }
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "selfSignedCertificate": {
                                                                    "description": "SelfSignedCertificate allows configuring the self-signed certificate generated by the operator.",
                                                                    "properties": {
                                                                        "disabled": {
                                                                            "description": "Disabled indicates that the provisioning of the self-signed certifcate should be disabled.",
                                                                            "type": "boolean",
                                                                        },
                                                                        "subjectAltNames": {
                                                                            "description": "SubjectAlternativeNames is a list of SANs to include in the generated HTTP TLS certificate.",
                                                                            "items": {
                                                                                "description": "SubjectAlternativeName represents a SAN entry in a x509 certificate.",
                                                                                "properties": {
                                                                                    "dns": {
                                                                                        "description": "DNS is the DNS name of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "ip": {
                                                                                        "description": "IP is the IP address of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                },
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "image": {
                                                    "description": "Image is the Kibana Docker image to deploy.",
                                                    "type": "string",
                                                },
                                                "monitoring": {
                                                    "description": "Monitoring enables you to collect and ship log and monitoring data of this Kibana. See https://www.elastic.co/guide/en/kibana/current/xpack-monitoring.html. Metricbeat and Filebeat are deployed in the same Pod as sidecars and each one sends data to one or two different Elasticsearch monitoring clusters running in the same Kubernetes cluster.",
                                                    "properties": {
                                                        "logs": {
                                                            "description": "Logs holds references to Elasticsearch clusters which receive log data from an associated resource.",
                                                            "properties": {
                                                                "elasticsearchRefs": {
                                                                    "description": "ElasticsearchRefs is a reference to a list of monitoring Elasticsearch clusters running in the same Kubernetes cluster. Due to existing limitations, only a single Elasticsearch cluster is currently supported.",
                                                                    "items": {
                                                                        "description": "ObjectSelector defines a reference to a Kubernetes object which can be an Elastic resource managed by the operator or a Secret describing an external Elastic resource not managed by the operator.",
                                                                        "properties": {
                                                                            "name": {
                                                                                "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                                                "type": "string",
                                                                            },
                                                                            "namespace": {
                                                                                "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                                                "type": "string",
                                                                            },
                                                                            "secretName": {
                                                                                "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                                                "type": "string",
                                                                            },
                                                                            "serviceName": {
                                                                                "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                                                "type": "string",
                                                                            },
                                                                        },
                                                                        "type": "object",
                                                                    },
                                                                    "type": "array",
                                                                }
                                                            },
                                                            "type": "object",
                                                        },
                                                        "metrics": {
                                                            "description": "Metrics holds references to Elasticsearch clusters which receive monitoring data from this resource.",
                                                            "properties": {
                                                                "elasticsearchRefs": {
                                                                    "description": "ElasticsearchRefs is a reference to a list of monitoring Elasticsearch clusters running in the same Kubernetes cluster. Due to existing limitations, only a single Elasticsearch cluster is currently supported.",
                                                                    "items": {
                                                                        "description": "ObjectSelector defines a reference to a Kubernetes object which can be an Elastic resource managed by the operator or a Secret describing an external Elastic resource not managed by the operator.",
                                                                        "properties": {
                                                                            "name": {
                                                                                "description": "Name of an existing Kubernetes object corresponding to an Elastic resource managed by ECK.",
                                                                                "type": "string",
                                                                            },
                                                                            "namespace": {
                                                                                "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                                                "type": "string",
                                                                            },
                                                                            "secretName": {
                                                                                "description": "SecretName is the name of an existing Kubernetes secret that contains connection information for associating an Elastic resource not managed by the operator. The referenced secret must contain the following: - `url`: the URL to reach the Elastic resource - `username`: the username of the user to be authenticated to the Elastic resource - `password`: the password of the user to be authenticated to the Elastic resource - `ca.crt`: the CA certificate in PEM format (optional). This field cannot be used in combination with the other fields name, namespace or serviceName.",
                                                                                "type": "string",
                                                                            },
                                                                            "serviceName": {
                                                                                "description": "ServiceName is the name of an existing Kubernetes service which is used to make requests to the referenced object. It has to be in the same namespace as the referenced resource. If left empty, the default HTTP service of the referenced resource is used.",
                                                                                "type": "string",
                                                                            },
                                                                        },
                                                                        "type": "object",
                                                                    },
                                                                    "type": "array",
                                                                }
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "podTemplate": {
                                                    "description": "PodTemplate provides customisation options (labels, annotations, affinity rules, resource requests, and so on) for the Kibana pods",
                                                    "type": "object",
                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                },
                                                "revisionHistoryLimit": {
                                                    "description": "RevisionHistoryLimit is the number of revisions to retain to allow rollback in the underlying Deployment.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "secureSettings": {
                                                    "description": "SecureSettings is a list of references to Kubernetes secrets containing sensitive configuration options for Kibana.",
                                                    "items": {
                                                        "description": "SecretSource defines a data source based on a Kubernetes Secret.",
                                                        "properties": {
                                                            "entries": {
                                                                "description": "Entries define how to project each key-value pair in the secret to filesystem paths. If not defined, all keys will be projected to similarly named paths in the filesystem. If defined, only the specified keys will be projected to the corresponding paths.",
                                                                "items": {
                                                                    "description": "KeyToPath defines how to map a key in a Secret object to a filesystem path.",
                                                                    "properties": {
                                                                        "key": {
                                                                            "description": "Key is the key contained in the secret.",
                                                                            "type": "string",
                                                                        },
                                                                        "path": {
                                                                            "description": 'Path is the relative file path to map the key to. Path must not be an absolute file path and must not contain any ".." components.',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "required": ["key"],
                                                                    "type": "object",
                                                                },
                                                                "type": "array",
                                                            },
                                                            "secretName": {
                                                                "description": "SecretName is the name of the secret.",
                                                                "type": "string",
                                                            },
                                                        },
                                                        "required": ["secretName"],
                                                        "type": "object",
                                                    },
                                                    "type": "array",
                                                },
                                                "serviceAccountName": {
                                                    "description": "ServiceAccountName is used to check access from the current resource to a resource (for ex. Elasticsearch) in a different namespace. Can only be used if ECK is enforcing RBAC on references.",
                                                    "type": "string",
                                                },
                                                "version": {
                                                    "description": "Version of Kibana.",
                                                    "type": "string",
                                                },
                                            },
                                            "required": ["version"],
                                            "type": "object",
                                        },
                                        "status": {
                                            "description": "KibanaStatus defines the observed state of Kibana",
                                            "properties": {
                                                "associationStatus": {
                                                    "description": "AssociationStatus is the status of any auto-linking to Elasticsearch clusters. This field is deprecated and will be removed in a future release. Use ElasticsearchAssociationStatus instead.",
                                                    "type": "string",
                                                },
                                                "availableNodes": {
                                                    "description": "AvailableNodes is the number of available replicas in the deployment.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "count": {
                                                    "description": "Count corresponds to Scale.Status.Replicas, which is the actual number of observed instances of the scaled object.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "elasticsearchAssociationStatus": {
                                                    "description": "ElasticsearchAssociationStatus is the status of any auto-linking to Elasticsearch clusters.",
                                                    "type": "string",
                                                },
                                                "enterpriseSearchAssociationStatus": {
                                                    "description": "EnterpriseSearchAssociationStatus is the status of any auto-linking to Enterprise Search.",
                                                    "type": "string",
                                                },
                                                "health": {
                                                    "description": "Health of the deployment.",
                                                    "type": "string",
                                                },
                                                "monitoringAssociationStatus": {
                                                    "additionalProperties": {
                                                        "description": "AssociationStatus is the status of an association resource.",
                                                        "type": "string",
                                                    },
                                                    "description": "MonitoringAssociationStatus is the status of any auto-linking to monitoring Elasticsearch clusters.",
                                                    "type": "object",
                                                },
                                                "observedGeneration": {
                                                    "description": "ObservedGeneration is the most recent generation observed for this Kibana instance. It corresponds to the metadata generation, which is updated on mutation by the API Server. If the generation observed in status diverges from the generation in metadata, the Kibana controller has not yet processed the changes contained in the Kibana specification.",
                                                    "format": "int64",
                                                    "type": "integer",
                                                },
                                                "selector": {
                                                    "description": "Selector is the label selector used to find all pods.",
                                                    "type": "string",
                                                },
                                                "version": {
                                                    "description": "Version of the stack resource currently running. During version upgrades, multiple versions may run in parallel: this value specifies the lowest version currently running.",
                                                    "type": "string",
                                                },
                                            },
                                            "type": "object",
                                        },
                                    },
                                    "type": "object",
                                }
                            },
                            "served": True,
                            "storage": True,
                            "subresources": {
                                "scale": {
                                    "labelSelectorPath": ".status.selector",
                                    "specReplicasPath": ".spec.count",
                                    "statusReplicasPath": ".status.count",
                                },
                                "status": {},
                            },
                        },
                        {
                            "additionalPrinterColumns": [
                                {
                                    "jsonPath": ".status.health",
                                    "name": "health",
                                    "type": "string",
                                },
                                {
                                    "description": "Available nodes",
                                    "jsonPath": ".status.availableNodes",
                                    "name": "nodes",
                                    "type": "integer",
                                },
                                {
                                    "description": "Kibana version",
                                    "jsonPath": ".spec.version",
                                    "name": "version",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".metadata.creationTimestamp",
                                    "name": "age",
                                    "type": "date",
                                },
                            ],
                            "name": "v1beta1",
                            "schema": {
                                "openAPIV3Schema": {
                                    "description": "Kibana represents a Kibana resource in a Kubernetes cluster.",
                                    "properties": {
                                        "apiVersion": {
                                            "description": "APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources",
                                            "type": "string",
                                        },
                                        "kind": {
                                            "description": "Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds",
                                            "type": "string",
                                        },
                                        "metadata": {"type": "object"},
                                        "spec": {
                                            "description": "KibanaSpec holds the specification of a Kibana instance.",
                                            "properties": {
                                                "config": {
                                                    "description": "Config holds the Kibana configuration. See: https://www.elastic.co/guide/en/kibana/current/settings.html",
                                                    "type": "object",
                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                },
                                                "count": {
                                                    "description": "Count of Kibana instances to deploy.",
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "elasticsearchRef": {
                                                    "description": "ElasticsearchRef is a reference to an Elasticsearch cluster running in the same Kubernetes cluster.",
                                                    "properties": {
                                                        "name": {
                                                            "description": "Name of the Kubernetes object.",
                                                            "type": "string",
                                                        },
                                                        "namespace": {
                                                            "description": "Namespace of the Kubernetes object. If empty, defaults to the current namespace.",
                                                            "type": "string",
                                                        },
                                                    },
                                                    "required": ["name"],
                                                    "type": "object",
                                                },
                                                "http": {
                                                    "description": "HTTP holds the HTTP layer configuration for Kibana.",
                                                    "properties": {
                                                        "service": {
                                                            "description": "Service defines the template for the associated Kubernetes Service object.",
                                                            "properties": {
                                                                "metadata": {
                                                                    "description": "ObjectMeta is the metadata of the service. The name and namespace provided here are managed by ECK and will be ignored.",
                                                                    "properties": {
                                                                        "annotations": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "finalizers": {
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "labels": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "name": {
                                                                            "type": "string"
                                                                        },
                                                                        "namespace": {
                                                                            "type": "string"
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "spec": {
                                                                    "description": "Spec is the specification of the service.",
                                                                    "properties": {
                                                                        "allocateLoadBalancerNodePorts": {
                                                                            "description": 'allocateLoadBalancerNodePorts defines if NodePorts will be automatically allocated for services with type LoadBalancer.  Default is "true". It may be set to "false" if the cluster load-balancer does not rely on NodePorts.  If the caller requests specific NodePorts (by specifying a value), those requests will be respected, regardless of this field. This field may only be set for services with type LoadBalancer and will be cleared if the type is changed to any other type.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "clusterIP": {
                                                                            "description": 'clusterIP is the IP address of the service and is usually assigned randomly. If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be blank) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address. Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "clusterIPs": {
                                                                            "description": 'ClusterIPs is a list of IP addresses assigned to this service, and are usually assigned randomly.  If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be allocated to the service; otherwise creation of the service will fail. This field may not be changed through updates unless the type field is also being changed to ExternalName (which requires this field to be empty) or the type field is being changed from ExternalName (in which case this field may optionally be specified, as describe above).  Valid values are "None", empty string (""), or a valid IP address.  Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint connections are preferred and proxying is not required.  Only applies to types ClusterIP, NodePort, and LoadBalancer. If this field is specified when creating a Service of type ExternalName, creation will fail. This field will be wiped when updating a Service to type ExternalName.  If this field is not specified, it will be initialized from the clusterIP field.  If this field is specified, clients must ensure that clusterIPs[0] and clusterIP have the same value. \n This field may hold a maximum of two entries (dual-stack IPs, in either order). These IPs must correspond to the values of the ipFamilies field. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "externalIPs": {
                                                                            "description": "externalIPs is a list of IP addresses for which nodes in the cluster will also accept traffic for this service.  These IPs are not managed by Kubernetes.  The user is responsible for ensuring that traffic arrives at a node with this IP.  A common example is external load-balancers that are not part of the Kubernetes system.",
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "externalName": {
                                                                            "description": 'externalName is the external reference that discovery mechanisms will return as an alias for this service (e.g. a DNS CNAME record). No proxying will be involved.  Must be a lowercase RFC-1123 hostname (https://tools.ietf.org/html/rfc1123) and requires `type` to be "ExternalName".',
                                                                            "type": "string",
                                                                        },
                                                                        "externalTrafficPolicy": {
                                                                            "description": 'externalTrafficPolicy describes how nodes distribute service traffic they receive on one of the Service\'s "externally-facing" addresses (NodePorts, ExternalIPs, and LoadBalancer IPs). If set to "Local", the proxy will configure the service in a way that assumes that external load balancers will take care of balancing the service traffic between nodes, and so each node will deliver traffic only to the node-local endpoints of the service, without masquerading the client source IP. (Traffic mistakenly sent to a node with no endpoints will be dropped.) The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features). Note that traffic sent to an External IP or LoadBalancer IP from within the cluster will always get "Cluster" semantics, but clients sending to a NodePort from within the cluster may need to take traffic policy into account when picking a node.',
                                                                            "type": "string",
                                                                        },
                                                                        "healthCheckNodePort": {
                                                                            "description": "healthCheckNodePort specifies the healthcheck nodePort for the service. This only applies when type is set to LoadBalancer and externalTrafficPolicy is set to Local. If a value is specified, is in-range, and is not in use, it will be used.  If not specified, a value will be automatically allocated.  External systems (e.g. load-balancers) can use this port to determine if a given node holds endpoints for this service or not.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type). This field cannot be updated once set.",
                                                                            "format": "int32",
                                                                            "type": "integer",
                                                                        },
                                                                        "internalTrafficPolicy": {
                                                                            "description": 'InternalTrafficPolicy describes how nodes distribute service traffic they receive on the ClusterIP. If set to "Local", the proxy will assume that pods only want to talk to endpoints of the service on the same node as the pod, dropping the traffic if there are no local endpoints. The default value, "Cluster", uses the standard behavior of routing to all endpoints evenly (possibly modified by topology and other features).',
                                                                            "type": "string",
                                                                        },
                                                                        "ipFamilies": {
                                                                            "description": 'IPFamilies is a list of IP families (e.g. IPv4, IPv6) assigned to this service. This field is usually assigned automatically based on cluster configuration and the ipFamilyPolicy field. If this field is specified manually, the requested family is available in the cluster, and ipFamilyPolicy allows it, it will be used; otherwise creation of the service will fail. This field is conditionally mutable: it allows for adding or removing a secondary IP family, but it does not allow changing the primary IP family of the Service. Valid values are "IPv4" and "IPv6".  This field only applies to Services of types ClusterIP, NodePort, and LoadBalancer, and does apply to "headless" services. This field will be wiped when updating a Service to type ExternalName. \n This field may hold a maximum of two entries (dual-stack families, in either order).  These families must correspond to the values of the clusterIPs field, if specified. Both clusterIPs and ipFamilies are governed by the ipFamilyPolicy field.',
                                                                            "items": {
                                                                                "description": "IPFamily represents the IP Family (IPv4 or IPv6). This type is used to express the family of an IP expressed by a type (e.g. service.spec.ipFamilies).",
                                                                                "type": "string",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-type": "atomic",
                                                                        },
                                                                        "ipFamilyPolicy": {
                                                                            "description": 'IPFamilyPolicy represents the dual-stack-ness requested or required by this Service. If there is no value provided, then this field will be set to SingleStack. Services can be "SingleStack" (a single IP family), "PreferDualStack" (two IP families on dual-stack configured clusters or a single IP family on single-stack clusters), or "RequireDualStack" (two IP families on dual-stack configured clusters, otherwise fail). The ipFamilies and clusterIPs fields depend on the value of this field. This field will be wiped when updating a service to type ExternalName.',
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerClass": {
                                                                            "description": "loadBalancerClass is the class of the load balancer implementation this Service belongs to. If specified, the value of this field must be a label-style identifier, with an optional prefix, e.g. \"internal-vip\" or \"example.com/internal-vip\". Unprefixed names are reserved for end-users. This field can only be set when the Service type is 'LoadBalancer'. If not set, the default load balancer implementation is used, today this is typically done through the cloud provider integration, but should apply for any default implementation. If set, it is assumed that a load balancer implementation is watching for Services with a matching class. Any default load balancer implementation (e.g. cloud providers) should ignore Services that set this field. This field can only be set when creating or updating a Service to type 'LoadBalancer'. Once set, it can not be changed. This field will be wiped when a service is updated to a non 'LoadBalancer' type.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerIP": {
                                                                            "description": "Only applies to Service Type: LoadBalancer. This feature depends on whether the underlying cloud-provider supports specifying the loadBalancerIP when a load balancer is created. This field will be ignored if the cloud-provider does not support the feature. Deprecated: This field was under-specified and its meaning varies across implementations, and it cannot support dual-stack. As of Kubernetes v1.24, users are encouraged to use implementation-specific annotations when available. This field may be removed in a future API version.",
                                                                            "type": "string",
                                                                        },
                                                                        "loadBalancerSourceRanges": {
                                                                            "description": 'If specified and supported by the platform, this will restrict traffic through the cloud-provider load-balancer will be restricted to the specified client IPs. This field will be ignored if the cloud-provider does not support the feature." More info: https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/',
                                                                            "items": {
                                                                                "type": "string"
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                        "ports": {
                                                                            "description": "The list of ports that are exposed by this service. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies",
                                                                            "items": {
                                                                                "description": "ServicePort contains information on service's port.",
                                                                                "properties": {
                                                                                    "appProtocol": {
                                                                                        "description": "The application protocol for this port. This field follows standard Kubernetes label syntax. Un-prefixed names are reserved for IANA standard service names (as per RFC-6335 and https://www.iana.org/assignments/service-names). Non-standard protocols should use prefixed names such as mycompany.com/my-custom-protocol.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "name": {
                                                                                        "description": "The name of this port within the service. This must be a DNS_LABEL. All ports within a ServiceSpec must have unique names. When considering the endpoints for a Service, this must match the 'name' field in the EndpointPort. Optional if only one ServicePort is defined on this service.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "nodePort": {
                                                                                        "description": "The port on each node on which this service is exposed when type is NodePort or LoadBalancer.  Usually assigned by the system. If a value is specified, in-range, and not in use it will be used, otherwise the operation will fail.  If not specified, a port will be allocated if this Service requires one.  If this field is specified when creating a Service which does not need it, creation will fail. This field will be wiped when updating a Service to no longer need it (e.g. changing type from NodePort to ClusterIP). More info: https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "port": {
                                                                                        "description": "The port that will be exposed by this service.",
                                                                                        "format": "int32",
                                                                                        "type": "integer",
                                                                                    },
                                                                                    "protocol": {
                                                                                        "default": "TCP",
                                                                                        "description": 'The IP protocol for this port. Supports "TCP", "UDP", and "SCTP". Default is TCP.',
                                                                                        "type": "string",
                                                                                    },
                                                                                    "targetPort": {
                                                                                        "anyOf": [
                                                                                            {
                                                                                                "type": "integer"
                                                                                            },
                                                                                            {
                                                                                                "type": "string"
                                                                                            },
                                                                                        ],
                                                                                        "description": "Number or name of the port to access on the pods targeted by the service. Number must be in the range 1 to 65535. Name must be an IANA_SVC_NAME. If this is a string, it will be looked up as a named port in the target Pod's container ports. If this is not specified, the value of the 'port' field is used (an identity map). This field is ignored for services with clusterIP=None, and should be omitted or set equal to the 'port' field. More info: https://kubernetes.io/docs/concepts/services-networking/service/#defining-a-service",
                                                                                        "x-kubernetes-int-or-string": True,
                                                                                    },
                                                                                },
                                                                                "required": [
                                                                                    "port"
                                                                                ],
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                            "x-kubernetes-list-map-keys": [
                                                                                "port",
                                                                                "protocol",
                                                                            ],
                                                                            "x-kubernetes-list-type": "map",
                                                                        },
                                                                        "publishNotReadyAddresses": {
                                                                            "description": 'publishNotReadyAddresses indicates that any agent which deals with endpoints for this Service should disregard any indications of ready/not-ready. The primary use case for setting this field is for a StatefulSet\'s Headless Service to propagate SRV DNS records for its Pods for the purpose of peer discovery. The Kubernetes controllers that generate Endpoints and EndpointSlice resources for Services interpret this to mean that all endpoints are considered "ready" even if the Pods themselves are not. Agents which consume only Kubernetes generated endpoints through the Endpoints or EndpointSlice resources can safely assume this behavior.',
                                                                            "type": "boolean",
                                                                        },
                                                                        "selector": {
                                                                            "additionalProperties": {
                                                                                "type": "string"
                                                                            },
                                                                            "description": "Route service traffic to pods with label keys and values matching this selector. If empty or not present, the service is assumed to have an external process managing its endpoints, which Kubernetes will not modify. Only applies to types ClusterIP, NodePort, and LoadBalancer. Ignored if type is ExternalName. More info: https://kubernetes.io/docs/concepts/services-networking/service/",
                                                                            "type": "object",
                                                                            "x-kubernetes-map-type": "atomic",
                                                                        },
                                                                        "sessionAffinity": {
                                                                            "description": 'Supports "ClientIP" and "None". Used to maintain session affinity. Enable client IP based session affinity. Must be ClientIP or None. Defaults to None. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies',
                                                                            "type": "string",
                                                                        },
                                                                        "sessionAffinityConfig": {
                                                                            "description": "sessionAffinityConfig contains the configurations of session affinity.",
                                                                            "properties": {
                                                                                "clientIP": {
                                                                                    "description": "clientIP contains the configurations of Client IP based session affinity.",
                                                                                    "properties": {
                                                                                        "timeoutSeconds": {
                                                                                            "description": 'timeoutSeconds specifies the seconds of ClientIP type session sticky time. The value must be >0 && <=86400(for 1 day) if ServiceAffinity == "ClientIP". Default value is 10800(for 3 hours).',
                                                                                            "format": "int32",
                                                                                            "type": "integer",
                                                                                        }
                                                                                    },
                                                                                    "type": "object",
                                                                                }
                                                                            },
                                                                            "type": "object",
                                                                        },
                                                                        "type": {
                                                                            "description": 'type determines how the Service is exposed. Defaults to ClusterIP. Valid options are ExternalName, ClusterIP, NodePort, and LoadBalancer. "ClusterIP" allocates a cluster-internal IP address for load-balancing to endpoints. Endpoints are determined by the selector or if that is not specified, by manual construction of an Endpoints object or EndpointSlice objects. If clusterIP is "None", no virtual IP is allocated and the endpoints are published as a set of endpoints rather than a virtual IP. "NodePort" builds on ClusterIP and allocates a port on every node which routes to the same endpoints as the clusterIP. "LoadBalancer" builds on NodePort and creates an external load-balancer (if supported in the current cloud) which routes to the same endpoints as the clusterIP. "ExternalName" aliases this service to the specified externalName. Several other fields do not apply to ExternalName services. More info: https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                        "tls": {
                                                            "description": "TLS defines options for configuring TLS for HTTP.",
                                                            "properties": {
                                                                "certificate": {
                                                                    "description": "Certificate is a reference to a Kubernetes secret that contains the certificate and private key for enabling TLS. The referenced secret should contain the following: \n - `ca.crt`: The certificate authority (optional). - `tls.crt`: The certificate (or a chain). - `tls.key`: The private key to the first certificate in the certificate chain.",
                                                                    "properties": {
                                                                        "secretName": {
                                                                            "description": "SecretName is the name of the secret.",
                                                                            "type": "string",
                                                                        }
                                                                    },
                                                                    "type": "object",
                                                                },
                                                                "selfSignedCertificate": {
                                                                    "description": "SelfSignedCertificate allows configuring the self-signed certificate generated by the operator.",
                                                                    "properties": {
                                                                        "disabled": {
                                                                            "description": "Disabled indicates that the provisioning of the self-signed certifcate should be disabled.",
                                                                            "type": "boolean",
                                                                        },
                                                                        "subjectAltNames": {
                                                                            "description": "SubjectAlternativeNames is a list of SANs to include in the generated HTTP TLS certificate.",
                                                                            "items": {
                                                                                "description": "SubjectAlternativeName represents a SAN entry in a x509 certificate.",
                                                                                "properties": {
                                                                                    "dns": {
                                                                                        "description": "DNS is the DNS name of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                    "ip": {
                                                                                        "description": "IP is the IP address of the subject.",
                                                                                        "type": "string",
                                                                                    },
                                                                                },
                                                                                "type": "object",
                                                                            },
                                                                            "type": "array",
                                                                        },
                                                                    },
                                                                    "type": "object",
                                                                },
                                                            },
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "image": {
                                                    "description": "Image is the Kibana Docker image to deploy.",
                                                    "type": "string",
                                                },
                                                "podTemplate": {
                                                    "description": "PodTemplate provides customisation options (labels, annotations, affinity rules, resource requests, and so on) for the Kibana pods",
                                                    "type": "object",
                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                },
                                                "secureSettings": {
                                                    "description": "SecureSettings is a list of references to Kubernetes secrets containing sensitive configuration options for Kibana.",
                                                    "items": {
                                                        "description": "SecretSource defines a data source based on a Kubernetes Secret.",
                                                        "properties": {
                                                            "entries": {
                                                                "description": "Entries define how to project each key-value pair in the secret to filesystem paths. If not defined, all keys will be projected to similarly named paths in the filesystem. If defined, only the specified keys will be projected to the corresponding paths.",
                                                                "items": {
                                                                    "description": "KeyToPath defines how to map a key in a Secret object to a filesystem path.",
                                                                    "properties": {
                                                                        "key": {
                                                                            "description": "Key is the key contained in the secret.",
                                                                            "type": "string",
                                                                        },
                                                                        "path": {
                                                                            "description": 'Path is the relative file path to map the key to. Path must not be an absolute file path and must not contain any ".." components.',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "required": ["key"],
                                                                    "type": "object",
                                                                },
                                                                "type": "array",
                                                            },
                                                            "secretName": {
                                                                "description": "SecretName is the name of the secret.",
                                                                "type": "string",
                                                            },
                                                        },
                                                        "required": ["secretName"],
                                                        "type": "object",
                                                    },
                                                    "type": "array",
                                                },
                                                "version": {
                                                    "description": "Version of Kibana.",
                                                    "type": "string",
                                                },
                                            },
                                            "type": "object",
                                        },
                                        "status": {
                                            "description": "KibanaStatus defines the observed state of Kibana",
                                            "properties": {
                                                "associationStatus": {
                                                    "description": "AssociationStatus is the status of an association resource.",
                                                    "type": "string",
                                                },
                                                "availableNodes": {
                                                    "format": "int32",
                                                    "type": "integer",
                                                },
                                                "health": {
                                                    "description": "KibanaHealth expresses the status of the Kibana instances.",
                                                    "type": "string",
                                                },
                                            },
                                            "type": "object",
                                        },
                                    },
                                    "type": "object",
                                }
                            },
                            "served": True,
                            "storage": False,
                            "subresources": {"status": {}},
                        },
                        {
                            "name": "v1alpha1",
                            "schema": {
                                "openAPIV3Schema": {
                                    "description": "to not break compatibility when upgrading from previous versions of the CRD",
                                    "type": "object",
                                }
                            },
                            "served": False,
                            "storage": False,
                        },
                    ],
                },
            },
        ],
        "Namespace": [
            {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": "elastic-system",
                    "labels": {"name": "elastic-system"},
                },
                "spec": {
                    "group": "stackconfigpolicy.k8s.elastic.co",
                    "names": {
                        "categories": ["elastic"],
                        "kind": "StackConfigPolicy",
                        "listKind": "StackConfigPolicyList",
                        "plural": "stackconfigpolicies",
                        "shortNames": ["scp"],
                        "singular": "stackconfigpolicy",
                    },
                    "scope": "Namespaced",
                    "versions": [
                        {
                            "additionalPrinterColumns": [
                                {
                                    "description": "Resources configured",
                                    "jsonPath": ".status.readyCount",
                                    "name": "Ready",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".status.phase",
                                    "name": "Phase",
                                    "type": "string",
                                },
                                {
                                    "jsonPath": ".metadata.creationTimestamp",
                                    "name": "Age",
                                    "type": "date",
                                },
                            ],
                            "name": "v1alpha1",
                            "schema": {
                                "openAPIV3Schema": {
                                    "description": "StackConfigPolicy represents a StackConfigPolicy resource in a Kubernetes cluster.",
                                    "properties": {
                                        "apiVersion": {
                                            "description": "APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources",
                                            "type": "string",
                                        },
                                        "kind": {
                                            "description": "Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds",
                                            "type": "string",
                                        },
                                        "metadata": {"type": "object"},
                                        "spec": {
                                            "properties": {
                                                "elasticsearch": {
                                                    "properties": {
                                                        "clusterSettings": {
                                                            "description": "ClusterSettings holds the Elasticsearch cluster settings (/_cluster/settings)",
                                                            "type": "object",
                                                            "x-kubernetes-preserve-unknown-fields": True,
                                                        },
                                                        "indexLifecyclePolicies": {
                                                            "description": "IndexLifecyclePolicies holds the Index Lifecycle policies settings (/_ilm/policy)",
                                                            "type": "object",
                                                            "x-kubernetes-preserve-unknown-fields": True,
                                                        },
                                                        "indexTemplates": {
                                                            "description": "IndexTemplates holds the Index and Component Templates settings",
                                                            "properties": {
                                                                "componentTemplates": {
                                                                    "description": "ComponentTemplates holds the Component Templates settings (/_component_template)",
                                                                    "type": "object",
                                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                                },
                                                                "composableIndexTemplates": {
                                                                    "description": "ComposableIndexTemplates holds the Index Templates settings (/_index_template)",
                                                                    "type": "object",
                                                                    "x-kubernetes-preserve-unknown-fields": True,
                                                                },
                                                            },
                                                            "type": "object",
                                                            "x-kubernetes-preserve-unknown-fields": True,
                                                        },
                                                        "ingestPipelines": {
                                                            "description": "IngestPipelines holds the Ingest Pipelines settings (/_ingest/pipeline)",
                                                            "type": "object",
                                                            "x-kubernetes-preserve-unknown-fields": True,
                                                        },
                                                        "securityRoleMappings": {
                                                            "description": "SecurityRoleMappings holds the Role Mappings settings (/_security/role_mapping)",
                                                            "type": "object",
                                                            "x-kubernetes-preserve-unknown-fields": True,
                                                        },
                                                        "snapshotLifecyclePolicies": {
                                                            "description": "SnapshotLifecyclePolicies holds the Snapshot Lifecycle Policies settings (/_slm/policy)",
                                                            "type": "object",
                                                            "x-kubernetes-preserve-unknown-fields": True,
                                                        },
                                                        "snapshotRepositories": {
                                                            "description": "SnapshotRepositories holds the Snapshot Repositories settings (/_snapshot)",
                                                            "type": "object",
                                                            "x-kubernetes-preserve-unknown-fields": True,
                                                        },
                                                    },
                                                    "type": "object",
                                                },
                                                "resourceSelector": {
                                                    "description": "A label selector is a label query over a set of resources. The result of matchLabels and matchExpressions are ANDed. An empty label selector matches all objects. A null label selector matches no objects.",
                                                    "properties": {
                                                        "matchExpressions": {
                                                            "description": "matchExpressions is a list of label selector requirements. The requirements are ANDed.",
                                                            "items": {
                                                                "description": "A label selector requirement is a selector that contains values, a key, and an operator that relates the key and values.",
                                                                "properties": {
                                                                    "key": {
                                                                        "description": "key is the label key that the selector applies to.",
                                                                        "type": "string",
                                                                    },
                                                                    "operator": {
                                                                        "description": "operator represents a key's relationship to a set of values. Valid operators are In, NotIn, Exists and DoesNotExist.",
                                                                        "type": "string",
                                                                    },
                                                                    "values": {
                                                                        "description": "values is an array of string values. If the operator is In or NotIn, the values array must be non-empty. If the operator is Exists or DoesNotExist, the values array must be empty. This array is replaced during a strategic merge patch.",
                                                                        "items": {
                                                                            "type": "string"
                                                                        },
                                                                        "type": "array",
                                                                    },
                                                                },
                                                                "required": [
                                                                    "key",
                                                                    "operator",
                                                                ],
                                                                "type": "object",
                                                            },
                                                            "type": "array",
                                                        },
                                                        "matchLabels": {
                                                            "additionalProperties": {
                                                                "type": "string"
                                                            },
                                                            "description": 'matchLabels is a map of {key,value} pairs. A single {key,value} in the matchLabels map is equivalent to an element of matchExpressions, whose key field is "key", the operator is "In", and the values array contains only "value". The requirements are ANDed.',
                                                            "type": "object",
                                                        },
                                                    },
                                                    "type": "object",
                                                    "x-kubernetes-map-type": "atomic",
                                                },
                                                "secureSettings": {
                                                    "items": {
                                                        "description": "SecretSource defines a data source based on a Kubernetes Secret.",
                                                        "properties": {
                                                            "entries": {
                                                                "description": "Entries define how to project each key-value pair in the secret to filesystem paths. If not defined, all keys will be projected to similarly named paths in the filesystem. If defined, only the specified keys will be projected to the corresponding paths.",
                                                                "items": {
                                                                    "description": "KeyToPath defines how to map a key in a Secret object to a filesystem path.",
                                                                    "properties": {
                                                                        "key": {
                                                                            "description": "Key is the key contained in the secret.",
                                                                            "type": "string",
                                                                        },
                                                                        "path": {
                                                                            "description": 'Path is the relative file path to map the key to. Path must not be an absolute file path and must not contain any ".." components.',
                                                                            "type": "string",
                                                                        },
                                                                    },
                                                                    "required": ["key"],
                                                                    "type": "object",
                                                                },
                                                                "type": "array",
                                                            },
                                                            "secretName": {
                                                                "description": "SecretName is the name of the secret.",
                                                                "type": "string",
                                                            },
                                                        },
                                                        "required": ["secretName"],
                                                        "type": "object",
                                                    },
                                                    "type": "array",
                                                },
                                            },
                                            "type": "object",
                                        },
                                        "status": {
                                            "properties": {
                                                "errors": {
                                                    "description": "Errors is the number of resources which have an incorrect configuration",
                                                    "type": "integer",
                                                },
                                                "observedGeneration": {
                                                    "description": "ObservedGeneration is the most recent generation observed for this StackConfigPolicy.",
                                                    "format": "int64",
                                                    "type": "integer",
                                                },
                                                "phase": {
                                                    "description": "Phase is the phase of the StackConfigPolicy.",
                                                    "type": "string",
                                                },
                                                "ready": {
                                                    "description": "Ready is the number of resources successfully configured.",
                                                    "type": "integer",
                                                },
                                                "readyCount": {
                                                    "description": "ReadyCount is a human representation of the number of resources successfully configured.",
                                                    "type": "string",
                                                },
                                                "resources": {
                                                    "description": "Resources is the number of resources to be configured.",
                                                    "type": "integer",
                                                },
                                                "resourcesStatuses": {
                                                    "additionalProperties": {
                                                        "description": "ResourcePolicyStatus models the status of the policy for one resource to be configured.",
                                                        "properties": {
                                                            "currentVersion": {
                                                                "format": "int64",
                                                                "type": "integer",
                                                            },
                                                            "error": {
                                                                "properties": {
                                                                    "message": {
                                                                        "type": "string"
                                                                    },
                                                                    "version": {
                                                                        "format": "int64",
                                                                        "type": "integer",
                                                                    },
                                                                },
                                                                "type": "object",
                                                            },
                                                            "expectedVersion": {
                                                                "format": "int64",
                                                                "type": "integer",
                                                            },
                                                            "phase": {"type": "string"},
                                                        },
                                                        "type": "object",
                                                    },
                                                    "description": "ResourcesStatuses holds the status for each resource to be configured.",
                                                    "type": "object",
                                                },
                                            },
                                            "required": ["resourcesStatuses"],
                                            "type": "object",
                                        },
                                    },
                                    "type": "object",
                                }
                            },
                            "served": True,
                            "storage": True,
                            "subresources": {"status": {}},
                        }
                    ],
                },
            }
        ],
        "ServiceAccount": [
            {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "name": "elastic-operator",
                    "namespace": "elastic-system",
                    "labels": {
                        "control-plane": "elastic-operator",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                },
            }
        ],
        "Secret": [
            {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": "elastic-webhook-server-cert",
                    "namespace": "elastic-system",
                    "labels": {
                        "control-plane": "elastic-operator",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                },
            }
        ],
        "ConfigMap": [
            {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "name": "elastic-operator",
                    "namespace": "elastic-system",
                    "labels": {
                        "control-plane": "elastic-operator",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                },
                "data": {
                    "eck.yaml": "log-verbosity: 0\nmetrics-port: 0\ncontainer-registry: docker.elastic.co\ncontainer-suffix: \nmax-concurrent-reconciles: 3\nca-cert-validity: 8760h\nca-cert-rotate-before: 24h\ncert-validity: 8760h\ncert-rotate-before: 24h\nexposed-node-labels: [topology.kubernetes.io/.*,failure-domain.beta.kubernetes.io/.*]\nset-default-security-context: auto-detect\nkube-client-timeout: 60s\nelasticsearch-client-timeout: 180s\ndisable-telemetry: false\ndistribution-channel: all-in-one\nvalidate-storage-class: true\nenable-webhook: true\nwebhook-name: elastic-webhook.k8s.elastic.co\nenable-leader-election: true\nelasticsearch-observation-interval: 10s"
                },
            }
        ],
        "ClusterRole": [
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRole",
                "metadata": {
                    "name": "elastic-operator",
                    "labels": {
                        "control-plane": "elastic-operator",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                },
                "rules": [
                    {
                        "apiGroups": ["authorization.k8s.io"],
                        "resources": ["subjectaccessreviews"],
                        "verbs": ["create"],
                    },
                    {
                        "apiGroups": ["coordination.k8s.io"],
                        "resources": ["leases"],
                        "verbs": ["create"],
                    },
                    {
                        "apiGroups": ["coordination.k8s.io"],
                        "resources": ["leases"],
                        "resourceNames": ["elastic-operator-leader"],
                        "verbs": ["get", "watch", "update"],
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["endpoints"],
                        "verbs": ["get", "list", "watch"],
                    },
                    {
                        "apiGroups": [""],
                        "resources": [
                            "pods",
                            "events",
                            "persistentvolumeclaims",
                            "secrets",
                            "services",
                            "configmaps",
                        ],
                        "verbs": [
                            "get",
                            "list",
                            "watch",
                            "create",
                            "update",
                            "patch",
                            "delete",
                        ],
                    },
                    {
                        "apiGroups": ["apps"],
                        "resources": ["deployments", "statefulsets", "daemonsets"],
                        "verbs": [
                            "get",
                            "list",
                            "watch",
                            "create",
                            "update",
                            "patch",
                            "delete",
                        ],
                    },
                    {
                        "apiGroups": ["policy"],
                        "resources": ["poddisruptionbudgets"],
                        "verbs": [
                            "get",
                            "list",
                            "watch",
                            "create",
                            "update",
                            "patch",
                            "delete",
                        ],
                    },
                    {
                        "apiGroups": ["elasticsearch.k8s.elastic.co"],
                        "resources": [
                            "elasticsearches",
                            "elasticsearches/status",
                            "elasticsearches/finalizers",
                        ],
                        "verbs": ["get", "list", "watch", "create", "update", "patch"],
                    },
                    {
                        "apiGroups": ["autoscaling.k8s.elastic.co"],
                        "resources": [
                            "elasticsearchautoscalers",
                            "elasticsearchautoscalers/status",
                            "elasticsearchautoscalers/finalizers",
                        ],
                        "verbs": ["get", "list", "watch", "create", "update", "patch"],
                    },
                    {
                        "apiGroups": ["kibana.k8s.elastic.co"],
                        "resources": [
                            "kibanas",
                            "kibanas/status",
                            "kibanas/finalizers",
                        ],
                        "verbs": ["get", "list", "watch", "create", "update", "patch"],
                    },
                    {
                        "apiGroups": ["apm.k8s.elastic.co"],
                        "resources": [
                            "apmservers",
                            "apmservers/status",
                            "apmservers/finalizers",
                        ],
                        "verbs": ["get", "list", "watch", "create", "update", "patch"],
                    },
                    {
                        "apiGroups": ["enterprisesearch.k8s.elastic.co"],
                        "resources": [
                            "enterprisesearches",
                            "enterprisesearches/status",
                            "enterprisesearches/finalizers",
                        ],
                        "verbs": ["get", "list", "watch", "create", "update", "patch"],
                    },
                    {
                        "apiGroups": ["beat.k8s.elastic.co"],
                        "resources": ["beats", "beats/status", "beats/finalizers"],
                        "verbs": ["get", "list", "watch", "create", "update", "patch"],
                    },
                    {
                        "apiGroups": ["agent.k8s.elastic.co"],
                        "resources": ["agents", "agents/status", "agents/finalizers"],
                        "verbs": ["get", "list", "watch", "create", "update", "patch"],
                    },
                    {
                        "apiGroups": ["maps.k8s.elastic.co"],
                        "resources": [
                            "elasticmapsservers",
                            "elasticmapsservers/status",
                            "elasticmapsservers/finalizers",
                        ],
                        "verbs": ["get", "list", "watch", "create", "update", "patch"],
                    },
                    {
                        "apiGroups": ["stackconfigpolicy.k8s.elastic.co"],
                        "resources": [
                            "stackconfigpolicies",
                            "stackconfigpolicies/status",
                            "stackconfigpolicies/finalizers",
                        ],
                        "verbs": ["get", "list", "watch", "create", "update", "patch"],
                    },
                    {
                        "apiGroups": ["storage.k8s.io"],
                        "resources": ["storageclasses"],
                        "verbs": ["get", "list", "watch"],
                    },
                    {
                        "apiGroups": ["admissionregistration.k8s.io"],
                        "resources": ["validatingwebhookconfigurations"],
                        "verbs": [
                            "get",
                            "list",
                            "watch",
                            "create",
                            "update",
                            "patch",
                            "delete",
                        ],
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["nodes"],
                        "verbs": ["get", "list", "watch"],
                    },
                ],
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRole",
                "metadata": {
                    "name": "elastic-operator-view",
                    "labels": {
                        "rbac.authorization.k8s.io/aggregate-to-view": "true",
                        "rbac.authorization.k8s.io/aggregate-to-edit": "true",
                        "rbac.authorization.k8s.io/aggregate-to-admin": "true",
                        "control-plane": "elastic-operator",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                },
                "rules": [
                    {
                        "apiGroups": ["elasticsearch.k8s.elastic.co"],
                        "resources": ["elasticsearches"],
                        "verbs": ["get", "list", "watch"],
                    },
                    {
                        "apiGroups": ["autoscaling.k8s.elastic.co"],
                        "resources": ["elasticsearchautoscalers"],
                        "verbs": ["get", "list", "watch"],
                    },
                    {
                        "apiGroups": ["apm.k8s.elastic.co"],
                        "resources": ["apmservers"],
                        "verbs": ["get", "list", "watch"],
                    },
                    {
                        "apiGroups": ["kibana.k8s.elastic.co"],
                        "resources": ["kibanas"],
                        "verbs": ["get", "list", "watch"],
                    },
                    {
                        "apiGroups": ["enterprisesearch.k8s.elastic.co"],
                        "resources": ["enterprisesearches"],
                        "verbs": ["get", "list", "watch"],
                    },
                    {
                        "apiGroups": ["beat.k8s.elastic.co"],
                        "resources": ["beats"],
                        "verbs": ["get", "list", "watch"],
                    },
                    {
                        "apiGroups": ["agent.k8s.elastic.co"],
                        "resources": ["agents"],
                        "verbs": ["get", "list", "watch"],
                    },
                    {
                        "apiGroups": ["maps.k8s.elastic.co"],
                        "resources": ["elasticmapsservers"],
                        "verbs": ["get", "list", "watch"],
                    },
                    {
                        "apiGroups": ["stackconfigpolicy.k8s.elastic.co"],
                        "resources": ["stackconfigpolicies"],
                        "verbs": ["get", "list", "watch"],
                    },
                ],
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRole",
                "metadata": {
                    "name": "elastic-operator-edit",
                    "labels": {
                        "rbac.authorization.k8s.io/aggregate-to-edit": "true",
                        "rbac.authorization.k8s.io/aggregate-to-admin": "true",
                        "control-plane": "elastic-operator",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                },
                "rules": [
                    {
                        "apiGroups": ["elasticsearch.k8s.elastic.co"],
                        "resources": ["elasticsearches"],
                        "verbs": [
                            "create",
                            "delete",
                            "deletecollection",
                            "patch",
                            "update",
                        ],
                    },
                    {
                        "apiGroups": ["autoscaling.k8s.elastic.co"],
                        "resources": ["elasticsearchautoscalers"],
                        "verbs": [
                            "create",
                            "delete",
                            "deletecollection",
                            "patch",
                            "update",
                        ],
                    },
                    {
                        "apiGroups": ["apm.k8s.elastic.co"],
                        "resources": ["apmservers"],
                        "verbs": [
                            "create",
                            "delete",
                            "deletecollection",
                            "patch",
                            "update",
                        ],
                    },
                    {
                        "apiGroups": ["kibana.k8s.elastic.co"],
                        "resources": ["kibanas"],
                        "verbs": [
                            "create",
                            "delete",
                            "deletecollection",
                            "patch",
                            "update",
                        ],
                    },
                    {
                        "apiGroups": ["enterprisesearch.k8s.elastic.co"],
                        "resources": ["enterprisesearches"],
                        "verbs": [
                            "create",
                            "delete",
                            "deletecollection",
                            "patch",
                            "update",
                        ],
                    },
                    {
                        "apiGroups": ["beat.k8s.elastic.co"],
                        "resources": ["beats"],
                        "verbs": [
                            "create",
                            "delete",
                            "deletecollection",
                            "patch",
                            "update",
                        ],
                    },
                    {
                        "apiGroups": ["agent.k8s.elastic.co"],
                        "resources": ["agents"],
                        "verbs": [
                            "create",
                            "delete",
                            "deletecollection",
                            "patch",
                            "update",
                        ],
                    },
                    {
                        "apiGroups": ["maps.k8s.elastic.co"],
                        "resources": ["elasticmapsservers"],
                        "verbs": [
                            "create",
                            "delete",
                            "deletecollection",
                            "patch",
                            "update",
                        ],
                    },
                    {
                        "apiGroups": ["stackconfigpolicy.k8s.elastic.co"],
                        "resources": ["stackconfigpolicies"],
                        "verbs": [
                            "create",
                            "delete",
                            "deletecollection",
                            "patch",
                            "update",
                        ],
                    },
                ],
            },
        ],
        "ClusterRoleBinding": [
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRoleBinding",
                "metadata": {
                    "name": "elastic-operator",
                    "labels": {
                        "control-plane": "elastic-operator",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                },
                "roleRef": {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": "ClusterRole",
                    "name": "elastic-operator",
                },
                "subjects": [
                    {
                        "kind": "ServiceAccount",
                        "name": "elastic-operator",
                        "namespace": "elastic-system",
                    }
                ],
            }
        ],
        "Service": [
            {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "elastic-webhook-server",
                    "namespace": "elastic-system",
                    "labels": {
                        "control-plane": "elastic-operator",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                },
                "spec": {
                    "ports": [{"name": "https", "port": 443, "targetPort": 9443}],
                    "selector": {"control-plane": "elastic-operator"},
                },
            }
        ],
        "StatefulSet": [
            {
                "apiVersion": "apps/v1",
                "kind": "StatefulSet",
                "metadata": {
                    "name": "elastic-operator",
                    "namespace": "elastic-system",
                    "labels": {
                        "control-plane": "elastic-operator",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                },
                "spec": {
                    "selector": {"matchLabels": {"control-plane": "elastic-operator"}},
                    "serviceName": "elastic-operator",
                    "replicas": 1,
                    "template": {
                        "metadata": {
                            "annotations": {
                                "co.elastic.logs/raw": '[{"type":"container","json.keys_under_root":true,"paths":["/var/log/containers/*${data.kubernetes.container.id}.log"],"processors":[{"convert":{"mode":"rename","ignore_missing":true,"fields":[{"from":"error","to":"_error"}]}},{"convert":{"mode":"rename","ignore_missing":true,"fields":[{"from":"_error","to":"error.message"}]}},{"convert":{"mode":"rename","ignore_missing":true,"fields":[{"from":"source","to":"_source"}]}},{"convert":{"mode":"rename","ignore_missing":true,"fields":[{"from":"_source","to":"event.source"}]}}]}]',
                                "checksum/config": "0167077654d0c8023b9201c09b02b9213c73d47b50aab990b1e2e8cd41653ca7",
                            },
                            "labels": {"control-plane": "elastic-operator"},
                        },
                        "spec": {
                            "terminationGracePeriodSeconds": 10,
                            "serviceAccountName": "elastic-operator",
                            "securityContext": {"runAsNonRoot": True},
                            "containers": [
                                {
                                    "image": "docker.elastic.co/eck/eck-operator:2.6.1",
                                    "imagePullPolicy": "IfNotPresent",
                                    "name": "manager",
                                    "args": ["manager", "--config=/conf/eck.yaml"],
                                    "securityContext": {
                                        "allowPrivilegeEscalation": False,
                                        "capabilities": {"drop": ["ALL"]},
                                        "readOnlyRootFilesystem": True,
                                        "runAsNonRoot": True,
                                    },
                                    "env": [
                                        {
                                            "name": "OPERATOR_NAMESPACE",
                                            "valueFrom": {
                                                "fieldRef": {
                                                    "fieldPath": "metadata.namespace"
                                                }
                                            },
                                        },
                                        {
                                            "name": "POD_IP",
                                            "valueFrom": {
                                                "fieldRef": {
                                                    "fieldPath": "status.podIP"
                                                }
                                            },
                                        },
                                        {
                                            "name": "WEBHOOK_SECRET",
                                            "value": "elastic-webhook-server-cert",
                                        },
                                    ],
                                    "resources": {
                                        "limits": {"cpu": 1, "memory": "1Gi"},
                                        "requests": {"cpu": "100m", "memory": "150Mi"},
                                    },
                                    "ports": [
                                        {
                                            "containerPort": 9443,
                                            "name": "https-webhook",
                                            "protocol": "TCP",
                                        }
                                    ],
                                    "volumeMounts": [
                                        {
                                            "mountPath": "/conf",
                                            "name": "conf",
                                            "readOnly": True,
                                        },
                                        {
                                            "mountPath": "/tmp/k8s-webhook-server/serving-certs",
                                            "name": "cert",
                                            "readOnly": True,
                                        },
                                    ],
                                }
                            ],
                            "volumes": [
                                {
                                    "name": "conf",
                                    "configMap": {"name": "elastic-operator"},
                                },
                                {
                                    "name": "cert",
                                    "secret": {
                                        "defaultMode": 420,
                                        "secretName": "elastic-webhook-server-cert",
                                    },
                                },
                            ],
                        },
                    },
                },
            }
        ],
        "ValidatingWebhookConfiguration": [
            {
                "apiVersion": "admissionregistration.k8s.io/v1",
                "kind": "ValidatingWebhookConfiguration",
                "metadata": {
                    "name": "elastic-webhook.k8s.elastic.co",
                    "labels": {
                        "control-plane": "elastic-operator",
                        "app.kubernetes.io/version": "2.6.1",
                    },
                },
                "webhooks": [
                    {
                        "clientConfig": {
                            "caBundle": "Cg==",
                            "service": {
                                "name": "elastic-webhook-server",
                                "namespace": "elastic-system",
                                "path": "/validate-agent-k8s-elastic-co-v1alpha1-agent",
                            },
                        },
                        "failurePolicy": "Ignore",
                        "name": "elastic-agent-validation-v1alpha1.k8s.elastic.co",
                        "matchPolicy": "Exact",
                        "admissionReviewVersions": ["v1beta1"],
                        "sideEffects": "None",
                        "rules": [
                            {
                                "apiGroups": ["agent.k8s.elastic.co"],
                                "apiVersions": ["v1alpha1"],
                                "operations": ["CREATE", "UPDATE"],
                                "resources": ["agents"],
                            }
                        ],
                    },
                    {
                        "clientConfig": {
                            "caBundle": "Cg==",
                            "service": {
                                "name": "elastic-webhook-server",
                                "namespace": "elastic-system",
                                "path": "/validate-apm-k8s-elastic-co-v1-apmserver",
                            },
                        },
                        "failurePolicy": "Ignore",
                        "name": "elastic-apm-validation-v1.k8s.elastic.co",
                        "matchPolicy": "Exact",
                        "admissionReviewVersions": ["v1beta1"],
                        "sideEffects": "None",
                        "rules": [
                            {
                                "apiGroups": ["apm.k8s.elastic.co"],
                                "apiVersions": ["v1"],
                                "operations": ["CREATE", "UPDATE"],
                                "resources": ["apmservers"],
                            }
                        ],
                    },
                    {
                        "clientConfig": {
                            "caBundle": "Cg==",
                            "service": {
                                "name": "elastic-webhook-server",
                                "namespace": "elastic-system",
                                "path": "/validate-apm-k8s-elastic-co-v1beta1-apmserver",
                            },
                        },
                        "failurePolicy": "Ignore",
                        "name": "elastic-apm-validation-v1beta1.k8s.elastic.co",
                        "matchPolicy": "Exact",
                        "admissionReviewVersions": ["v1beta1"],
                        "sideEffects": "None",
                        "rules": [
                            {
                                "apiGroups": ["apm.k8s.elastic.co"],
                                "apiVersions": ["v1beta1"],
                                "operations": ["CREATE", "UPDATE"],
                                "resources": ["apmservers"],
                            }
                        ],
                    },
                    {
                        "clientConfig": {
                            "caBundle": "Cg==",
                            "service": {
                                "name": "elastic-webhook-server",
                                "namespace": "elastic-system",
                                "path": "/validate-beat-k8s-elastic-co-v1beta1-beat",
                            },
                        },
                        "failurePolicy": "Ignore",
                        "name": "elastic-beat-validation-v1beta1.k8s.elastic.co",
                        "matchPolicy": "Exact",
                        "admissionReviewVersions": ["v1beta1"],
                        "sideEffects": "None",
                        "rules": [
                            {
                                "apiGroups": ["beat.k8s.elastic.co"],
                                "apiVersions": ["v1beta1"],
                                "operations": ["CREATE", "UPDATE"],
                                "resources": ["beats"],
                            }
                        ],
                    },
                    {
                        "clientConfig": {
                            "caBundle": "Cg==",
                            "service": {
                                "name": "elastic-webhook-server",
                                "namespace": "elastic-system",
                                "path": "/validate-enterprisesearch-k8s-elastic-co-v1-enterprisesearch",
                            },
                        },
                        "failurePolicy": "Ignore",
                        "name": "elastic-ent-validation-v1.k8s.elastic.co",
                        "matchPolicy": "Exact",
                        "admissionReviewVersions": ["v1beta1"],
                        "sideEffects": "None",
                        "rules": [
                            {
                                "apiGroups": ["enterprisesearch.k8s.elastic.co"],
                                "apiVersions": ["v1"],
                                "operations": ["CREATE", "UPDATE"],
                                "resources": ["enterprisesearches"],
                            }
                        ],
                    },
                    {
                        "clientConfig": {
                            "caBundle": "Cg==",
                            "service": {
                                "name": "elastic-webhook-server",
                                "namespace": "elastic-system",
                                "path": "/validate-enterprisesearch-k8s-elastic-co-v1beta1-enterprisesearch",
                            },
                        },
                        "failurePolicy": "Ignore",
                        "name": "elastic-ent-validation-v1beta1.k8s.elastic.co",
                        "matchPolicy": "Exact",
                        "admissionReviewVersions": ["v1beta1"],
                        "sideEffects": "None",
                        "rules": [
                            {
                                "apiGroups": ["enterprisesearch.k8s.elastic.co"],
                                "apiVersions": ["v1beta1"],
                                "operations": ["CREATE", "UPDATE"],
                                "resources": ["enterprisesearches"],
                            }
                        ],
                    },
                    {
                        "clientConfig": {
                            "caBundle": "Cg==",
                            "service": {
                                "name": "elastic-webhook-server",
                                "namespace": "elastic-system",
                                "path": "/validate-elasticsearch-k8s-elastic-co-v1-elasticsearch",
                            },
                        },
                        "failurePolicy": "Ignore",
                        "name": "elastic-es-validation-v1.k8s.elastic.co",
                        "matchPolicy": "Exact",
                        "admissionReviewVersions": ["v1beta1"],
                        "sideEffects": "None",
                        "rules": [
                            {
                                "apiGroups": ["elasticsearch.k8s.elastic.co"],
                                "apiVersions": ["v1"],
                                "operations": ["CREATE", "UPDATE"],
                                "resources": ["elasticsearches"],
                            }
                        ],
                    },
                    {
                        "clientConfig": {
                            "caBundle": "Cg==",
                            "service": {
                                "name": "elastic-webhook-server",
                                "namespace": "elastic-system",
                                "path": "/validate-elasticsearch-k8s-elastic-co-v1beta1-elasticsearch",
                            },
                        },
                        "failurePolicy": "Ignore",
                        "name": "elastic-es-validation-v1beta1.k8s.elastic.co",
                        "matchPolicy": "Exact",
                        "admissionReviewVersions": ["v1beta1"],
                        "sideEffects": "None",
                        "rules": [
                            {
                                "apiGroups": ["elasticsearch.k8s.elastic.co"],
                                "apiVersions": ["v1beta1"],
                                "operations": ["CREATE", "UPDATE"],
                                "resources": ["elasticsearches"],
                            }
                        ],
                    },
                    {
                        "clientConfig": {
                            "caBundle": "Cg==",
                            "service": {
                                "name": "elastic-webhook-server",
                                "namespace": "elastic-system",
                                "path": "/validate-kibana-k8s-elastic-co-v1-kibana",
                            },
                        },
                        "failurePolicy": "Ignore",
                        "name": "elastic-kb-validation-v1.k8s.elastic.co",
                        "matchPolicy": "Exact",
                        "admissionReviewVersions": ["v1beta1"],
                        "sideEffects": "None",
                        "rules": [
                            {
                                "apiGroups": ["kibana.k8s.elastic.co"],
                                "apiVersions": ["v1"],
                                "operations": ["CREATE", "UPDATE"],
                                "resources": ["kibanas"],
                            }
                        ],
                    },
                    {
                        "clientConfig": {
                            "caBundle": "Cg==",
                            "service": {
                                "name": "elastic-webhook-server",
                                "namespace": "elastic-system",
                                "path": "/validate-kibana-k8s-elastic-co-v1beta1-kibana",
                            },
                        },
                        "failurePolicy": "Ignore",
                        "name": "elastic-kb-validation-v1beta1.k8s.elastic.co",
                        "matchPolicy": "Exact",
                        "admissionReviewVersions": ["v1beta1"],
                        "sideEffects": "None",
                        "rules": [
                            {
                                "apiGroups": ["kibana.k8s.elastic.co"],
                                "apiVersions": ["v1beta1"],
                                "operations": ["CREATE", "UPDATE"],
                                "resources": ["kibanas"],
                            }
                        ],
                    },
                    {
                        "clientConfig": {
                            "caBundle": "Cg==",
                            "service": {
                                "name": "elastic-webhook-server",
                                "namespace": "elastic-system",
                                "path": "/validate-autoscaling-k8s-elastic-co-v1alpha1-elasticsearchautoscaler",
                            },
                        },
                        "failurePolicy": "Ignore",
                        "name": "elastic-esa-validation-v1alpha1.k8s.elastic.co",
                        "matchPolicy": "Exact",
                        "admissionReviewVersions": ["v1beta1"],
                        "sideEffects": "None",
                        "rules": [
                            {
                                "apiGroups": ["autoscaling.k8s.elastic.co"],
                                "apiVersions": ["v1alpha1"],
                                "operations": ["CREATE", "UPDATE"],
                                "resources": ["elasticsearchautoscalers"],
                            }
                        ],
                    },
                    {
                        "clientConfig": {
                            "caBundle": "Cg==",
                            "service": {
                                "name": "elastic-webhook-server",
                                "namespace": "elastic-system",
                                "path": "/validate-scp-k8s-elastic-co-v1alpha1-stackconfigpolicies",
                            },
                        },
                        "failurePolicy": "Ignore",
                        "name": "elastic-scp-validation-v1alpha1.k8s.elastic.co",
                        "matchPolicy": "Exact",
                        "admissionReviewVersions": ["v1", "v1beta1"],
                        "sideEffects": "None",
                        "rules": [
                            {
                                "apiGroups": ["stackconfigpolicy.k8s.elastic.co"],
                                "apiVersions": ["v1alpha1"],
                                "operations": ["CREATE", "UPDATE"],
                                "resources": ["stackconfigpolicies"],
                            }
                        ],
                    },
                ],
            }
        ],
    }

    ###############################################################################################################
    # ------------------------------------------------ DATABASE ------------------------------------------------- #
    ###############################################################################################################

    DATABASE_MANIFEST = {
        "Service": [
            {
                "kind": "Service",
                "apiVersion": "v1",
                "metadata": {"name": "jaseci-db", "creationTimestamp": "None"},
                "spec": {
                    "ports": [{"protocol": "TCP", "port": 5432, "targetPort": 5432}],
                    "selector": {"pod": "jaseci-db"},
                    "type": "ClusterIP",
                    "sessionAffinity": "None",
                    "internalTrafficPolicy": "Cluster",
                },
                "status": {"loadBalancer": {}},
            }
        ],
        "Secret": [
            {
                "kind": "Secret",
                "apiVersion": "v1",
                "metadata": {
                    "name": "jaseci-db-credentials",
                    "creationTimestamp": "None",
                },
                "data": {
                    "password": "bGlmZWxvZ2lmeWphc2VjaQ==",
                    "user": "cG9zdGdyZXM=",
                },
                "type": "Opaque",
            }
        ],
        "PersistentVolumeClaim": [
            {
                "kind": "PersistentVolumeClaim",
                "apiVersion": "v1",
                "metadata": {"name": "jaseci-db-pvc", "creationTimestamp": "None"},
                "spec": {
                    "accessModes": ["ReadWriteOnce"],
                    "resources": {"requests": {"storage": "10Gi"}},
                    "volumeMode": "Filesystem",
                },
                "status": {"phase": "Pending"},
            }
        ],
        "Deployment": [
            {
                "kind": "Deployment",
                "apiVersion": "apps/v1",
                "metadata": {"name": "jaseci-db", "creationTimestamp": "None"},
                "spec": {
                    "replicas": 1,
                    "selector": {"matchLabels": {"pod": "jaseci-db"}},
                    "template": {
                        "metadata": {
                            "creationTimestamp": "None",
                            "labels": {"pod": "jaseci-db"},
                        },
                        "spec": {
                            "volumes": [
                                {
                                    "name": "jaseci-db-volume",
                                    "persistentVolumeClaim": {
                                        "claimName": "jaseci-db-pvc"
                                    },
                                }
                            ],
                            "containers": [
                                {
                                    "name": "jaseci-db",
                                    "image": "postgres:alpine",
                                    "ports": [
                                        {"containerPort": 5432, "protocol": "TCP"}
                                    ],
                                    "env": [
                                        {
                                            "name": "POSTGRES_USER",
                                            "valueFrom": {
                                                "secretKeyRef": {
                                                    "name": "jaseci-db-credentials",
                                                    "key": "user",
                                                }
                                            },
                                        },
                                        {
                                            "name": "POSTGRES_PASSWORD",
                                            "valueFrom": {
                                                "secretKeyRef": {
                                                    "name": "jaseci-db-credentials",
                                                    "key": "password",
                                                }
                                            },
                                        },
                                    ],
                                    "resources": {},
                                    "volumeMounts": [
                                        {
                                            "name": "jaseci-db-volume",
                                            "mountPath": "/var/lib/postgresql/data",
                                            "subPath": "jaseci",
                                        }
                                    ],
                                    "terminationMessagePath": "/dev/termination-log",
                                    "terminationMessagePolicy": "File",
                                    "imagePullPolicy": "IfNotPresent",
                                }
                            ],
                            "restartPolicy": "Always",
                            "terminationGracePeriodSeconds": 30,
                            "dnsPolicy": "ClusterFirst",
                            "securityContext": {},
                            "schedulerName": "default-scheduler",
                        },
                    },
                    "strategy": {
                        "type": "RollingUpdate",
                        "rollingUpdate": {"maxUnavailable": "25%", "maxSurge": "25%"},
                    },
                    "revisionHistoryLimit": 10,
                    "progressDeadlineSeconds": 600,
                },
                "status": {},
            }
        ],
    }
