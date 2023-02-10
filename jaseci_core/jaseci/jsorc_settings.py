import os


class JsOrcSettings:
    ###############################################################################################################
    # ------------------------------------------------- DEFAULT ------------------------------------------------- #
    ###############################################################################################################

    DEFAULT_CONFIG = {}
    DEFAULT_MANIFEST = {}

    UNSAFE_PARAPHRASE = "I know what I'm doing!"
    UNSAFE_KINDS = ["PersistentVolumeClaim"]

    ###############################################################################################################
    # -------------------------------------------------- JSORC -------------------------------------------------- #
    ###############################################################################################################

    KUBERNETES_CONFIG = {"in_cluster": True, "config": None}

    JSORC_CONFIG = {
        "automation": False,
        "backoff_interval": 10,
        "namespace": "default",
        "keep_alive": ["promon", "redis", "task", "mail", "elastic"],
        "kubernetes": KUBERNETES_CONFIG,
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
        "automated": False,
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

    ELASTIC_MANIFEST = {}
