from datetime import datetime
from .jsorc_settings import JsOrcSettings
from .svc.common_svc import CommonService
from .svc.proxy_svc import ProxyService


class JsOrc:
    _services = {}
    _repositories = {}
    _configs = {}
    _manifests = {}
    _instance = {}
    _settings = JsOrcSettings

    _lock = False

    @staticmethod
    def run(runner):
        runner()

    @staticmethod
    def push(name: str, target: dict, entry: dict):
        if name not in target:
            target[name] = [entry]
        else:
            target[name] = {
                key: rep
                for key, rep in sorted(
                    target[name] + [entry],
                    key=lambda item: (-item["priority"], -item["date_added"]),
                )
            }

    #################################################
    #                    GETTER                     #
    #################################################

    @classmethod
    def repo(cls, repository: str, *args, **kwargs):
        if repository not in cls._repositories:
            raise Exception(f"Repository {repository} is not existing!")

        # highest priority
        repository = cls._repositories[repository][0]

        return repository["type"](*args, **kwargs)

    @classmethod
    def serv(cls, service: str) -> CommonService:
        if service not in cls._services:
            raise Exception(f"Service {service} is not existing!")

        if service not in cls._instance:
            # highest priority
            instance = cls._services[service][0]

            cls._lock = True
            hook = cls.repo("hook")
            cls._lock = False

            config = hook.service_glob(
                instance["config"],
                cls.settings(instance["config"], cls.settings("DEFAULT_CONFIG")),
            )
            manifest = hook.service_glob(
                instance["manifest"],
                cls.settings(instance["manifest"], cls.settings("DEFAULT_MANIFEST")),
            )

            cls._instance[service] = instance["type"](config, manifest)

        return cls._instance[service]

    @classmethod
    def serv_reset(cls, service) -> CommonService:
        del cls._instance[service]
        return cls.serv(service)

    #################################################
    #                  DECORATORS                   #
    #################################################

    @classmethod
    def service(
        cls,
        name: str = None,
        config: str = None,
        manifest: str = None,
        priority: int = 0,
    ):
        def decorator(service: type):
            cls.push(
                name=name or service.__name__,
                target=cls._services,
                entry={
                    # override service to extend from CommonService
                    "type": service.__class__(
                        service.__name__ + "Proxy", (service, CommonService), {}
                    ),
                    "config": config or f"{name.upper()}_CONFIG",
                    "manifest": manifest or f"{name.upper()}_MANIFEST",
                    "priority": priority,
                    "date_added": int(datetime.utcnow().timestamp() * 1000),
                },
            )
            return service

        return decorator

    @classmethod
    def repository(cls, name: str = None, priority: int = 0):
        def decorator(repository: type):
            cls.push(
                name=name or repository.__name__,
                target=cls._repositories,
                entry={
                    "type": repository,
                    "priority": priority,
                    "date_added": int(datetime.utcnow().timestamp() * 1000),
                },
            )
            return repository

        return decorator

    @classmethod
    def inject(
        cls, repositories: list = [], services: list = [], lock_check: bool = False
    ):
        def decorator(callable):
            def argument_handler(*args, **kwargs):
                _instances = {}
                if lock_check and cls._lock:
                    proxy = ProxyService()
                    for repository in repositories:
                        _instances[repository] = proxy
                    for service in services:
                        _instances[service] = proxy
                else:
                    for repository in repositories:
                        _instances[repository] = cls.repo(repository)
                    for service in services:
                        _instances[service] = cls.serv(service)

                kwargs.update(_instances)
                callable(*args, **kwargs)

            return argument_handler

        return decorator

    @classmethod
    def settings(cls, name: str, default=None):
        return getattr(cls._services, name, default)
