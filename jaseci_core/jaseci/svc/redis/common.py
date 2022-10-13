from .kube import REDIS_KUBE


REDIS_CONFIG = {
    "enabled": True,
    "quiet": True,
    "host": "localhost",
    "port": "6379",
    "db": "1",
    "kube": REDIS_KUBE,
}
