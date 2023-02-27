import os
import re

from time import time
from yaml import safe_load_all, YAMLError

placeholder_full = re.compile(r"^\$j\{(.*?)\}$")
placeholder_partial = re.compile(r"\$j\{(.*?)\}")
placeholder_splitter = re.compile(r"\.?([^\.\[\"\]]+)(?:\[\"?([^\"\]]+)\"?\])?")
# original
# placeholder_splitter = re.compile(r"([^\.\[\"\]]+)(?:\[\"?([^\"\]]+)\"?\])?(?:\.([^\.\[\"\]]+))?")


def get_splitter(val: str):
    matches = placeholder_splitter.findall(val)
    _matches = []
    for match in matches:
        for m in match:
            if m:
                _matches.append(m)
    return _matches


def get_value(source: dict, keys: list):
    if keys:
        key = keys.pop(0)
        if key in source:
            if keys:
                if isinstance(source[key], dict):
                    return get_value(source[key], keys)
            else:
                return source[key]
    return None


def parse(manifest, data: dict or list):
    for k, d in data.items() if isinstance(data, dict) else enumerate(data):
        if isinstance(d, (dict, list)):
            parse(manifest, d)
        elif isinstance(d, str):
            matcher = placeholder_full.search(d)
            if matcher:
                keys = get_splitter(matcher.group(1))
                data[k] = get_value(manifest, keys)
            else:
                for matcher in placeholder_partial.findall(d):
                    keys = get_splitter(matcher)
                    data[k] = data[k].replace(
                        "$j{" + matcher + "}", get_value(manifest, keys)
                    )


def convert_yaml_manifest(file):
    manifest = {}
    try:
        for conf in safe_load_all(file):
            kind = conf["kind"]
            if not manifest.get(kind):
                manifest[kind] = {}
            manifest[kind].update({conf["metadata"]["name"]: conf})
    except YAMLError as exc:
        manifest = {"error": f"{exc}"}

    parse(manifest, manifest)

    return manifest


def load_default_yaml(file):
    manifest = {}
    with open(
        f"{os.path.dirname(os.path.abspath(__file__))}/manifests/{file}.yaml", "r"
    ) as stream:
        manifest = convert_yaml_manifest(stream)

    return manifest


class JsOrcSettings:
    ###############################################################################################################
    # ------------------------------------------------- DEFAULT ------------------------------------------------- #
    ###############################################################################################################

    DEFAULT_CONFIG = {"enabled": False, "quiet": False, "automated": False}

    DEFAULT_MANIFEST = {}

    UNSAFE_PARAPHRASE = "I know what I'm doing!"
    UNSAFE_KINDS = ["PersistentVolumeClaim"]

    SERVICE_MANIFEST_MAP = {}
    for svc in os.getenv("MANUAL_SERVICES", "").split(","):
        svc = svc.strip()
        if svc:
            SERVICE_MANIFEST_MAP[svc] = 0

    for svc in os.getenv("DEDICATED_PREFIXED_SERVICES", "").split(","):
        svc = svc.strip()
        if svc:
            SERVICE_MANIFEST_MAP[svc] = 2

    ###############################################################################################################
    # -------------------------------------------------- JSORC -------------------------------------------------- #
    ###############################################################################################################

    JSORC_CONFIG = {
        "backoff_interval": 10,
        "pre_loaded_services": ["redis", "prome", "mail", "task", "elastic"],
    }

    ###############################################################################################################
    # -------------------------------------------------- KUBE --------------------------------------------------- #
    ###############################################################################################################

    KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE", f"jaseci-{int(time() * 100000)}")

    KUBE_CONFIG = {
        "enabled": bool(os.getenv("KUBE_NAMESPACE")),
        "quiet": True,
        "automated": False,
        "namespace": KUBE_NAMESPACE,
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

    REDIS_MANIFEST = load_default_yaml("redis")

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
    # -------------------------------------------------- MAIL --------------------------------------------------- #
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
    # ------------------------------------------------- STRIPE -------------------------------------------------- #
    ###############################################################################################################

    STRIPE_CONFIG = {
        "enabled": False,
        "api_key": None,
        "automated": False,
        "webhook_key": None,
        "fallback_walker": "stripe",
        "event_walker": {},
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

    PROME_MANIFEST = load_default_yaml("prometheus")

    ###############################################################################################################
    # ------------------------------------------------ ELASTIC -------------------------------------------------- #
    ###############################################################################################################

    ELASTIC_CONFIG = {
        "enabled": bool(os.getenv("ELASTIC_HOST")),
        "quiet": False,
        "automated": True,
        "url": (
            f'https://{os.getenv("ELASTIC_HOST", "localhost")}'
            f':{os.getenv("ELASTIC_PORT", "9200")}'
        ),
        "auth": os.getenv("ELASTIC_AUTH"),
        "common_index": f"{KUBE_NAMESPACE}-common",
        "activity_index": f"{KUBE_NAMESPACE}-activity",
    }

    ELASTIC_MANIFEST = load_default_yaml("elastic")

    ###############################################################################################################
    # ------------------------------------------------ DATABASE ------------------------------------------------- #
    ###############################################################################################################

    DB_REGEN_CONFIG = {
        "enabled": os.environ.get("JSORC_DB_REGEN") == "true",
        "host": os.environ.get("POSTGRES_HOST", "jaseci-db"),
        "db": os.environ.get("DBNAME", "postgres"),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
        "port": os.getenv("POSTGRES_PORT", 5432),
    }

    DB_REGEN_MANIFEST = load_default_yaml("database")
