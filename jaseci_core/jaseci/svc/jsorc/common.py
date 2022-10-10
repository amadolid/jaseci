################################################
#                   DEFAULTS                   #
################################################

JSORC_CONFIG = {
    "enabled": True,
    "quiet": False,
    "interval": 10,
    "namespace": "default",
    "keep_alive": ["redis"],
}


class JsOrcProperties:
    def __init__(self, cls):
        if not hasattr(cls, "_interval"):
            setattr(cls, "_interval", 10)
            setattr(cls, "_namespace", "default")
            setattr(cls, "_keep_alive", [])

    @property
    def interval(self) -> int:
        return self.cls._interval

    @interval.setter
    def interval(self, val: int):
        self.cls._interval = val

    @property
    def namespace(self) -> str:
        return self.cls._namespace

    @namespace.setter
    def namespace(self, val: str):
        self.cls._namespace = val

    @property
    def keep_alive(self) -> list:
        return self.cls._keep_alive

    @keep_alive.setter
    def keep_alive(self, val: list):
        self.cls._keep_alive = val
