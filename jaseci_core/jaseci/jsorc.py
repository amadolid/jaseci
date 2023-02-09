from datetime import datetime
from .jsorc_settings import JsOrcSettings
from .svc.common_svc import CommonService
from .svc.proxy_svc import ProxyService
from typing import TypeVar, Any, Union

T = TypeVar("T")


class JsOrc:
    _contexts = {}
    _services = {}
    _repositories = {}
    _configs = {}
    _manifests = {}
    _instance = {}
    _settings = JsOrcSettings

    _use_proxy = False

    # ------------------ COMMONS ------------------ #

    __proxy__ = ProxyService()

    @staticmethod
    def run(runner):
        runner()

    @staticmethod
    def push(name: str, target: dict, entry: dict):
        if name not in target:
            target[name] = [entry]
        else:
            target[name] = sorted(
                target[name] + [entry],
                key=lambda item: (-item["priority"], -item["date_added"]),
            )

    #################################################
    #                    GETTER                     #
    #################################################

    # ------------------ context ------------------ #

    @classmethod
    def ctx(cls, context: str, cast: T = None, *args, **kwargs) -> Union[T, Any]:
        if context not in cls._contexts:
            raise Exception(f"Context {context} is not existing!")

        # highest priority
        context = cls._contexts[context][0]

        return context["type"](*args, **kwargs)

    @classmethod
    def ctx_cls(cls, context: str):
        if context not in cls._contexts:
            raise Exception(f"Context {context} is not existing!")

        return cls._contexts[context][0]["type"]

    @classmethod
    def master(cls, cast: T = None, *args, **kwargs) -> Union[T, Any]:
        return cls.gen_with_hook("master", cast, *args, **kwargs)

    @classmethod
    def super_master(cls, cast: T = None, *args, **kwargs) -> Union[T, Any]:
        return cls.gen_with_hook("super_master", cast, *args, **kwargs)

    @classmethod
    def gen_with_hook(cls, context: str, *args, **kwargs):
        if not kwargs.get("h", None):
            kwargs["h"] = cls.src("hook")

        return cls.ctx(context, None, *args, **kwargs)

    # ------------------ service ------------------ #

    @classmethod
    def svc(cls, service: str, caster: T = None) -> Union[T, CommonService]:
        if service not in cls._services:
            raise Exception(f"Service {service} is not existing!")

        if service not in cls._instance:
            # highest priority
            instance = cls._services[service][0]

            cls._use_proxy = True
            hook = cls.src("hook")
            cls._use_proxy = False

            config = hook.service_glob(
                instance["config"],
                cls.settings(instance["config"], cls.settings("DEFAULT_CONFIG")),
            )
            manifest = hook.service_glob(
                instance["manifest"],
                cls.settings(instance["manifest"], cls.settings("DEFAULT_MANIFEST")),
            )

            cls._instance[service] = instance["type"](config, manifest or {})

        return cls._instance[service]

    @classmethod
    def svc_cls(cls, service: str):
        if service not in cls._services:
            raise Exception(f"Service {service} is not existing!")

        return cls._services[service][0]["type"]

    @classmethod
    def svc_reset(cls, service, caster: T = None) -> Union[T, CommonService]:
        del cls._instance[service]
        return cls.svc(service)

    # ---------------- repository ----------------- #

    @classmethod
    def src(cls, repository: str, cast: T = None) -> Union[T, Any]:
        if repository not in cls._repositories:
            raise Exception(f"Repository {repository} is not existing!")

        # highest priority
        repository = cls._repositories[repository][0]

        return repository["type"]()

    @classmethod
    def hook(cls, cast: T = None) -> Union[T, Any]:
        return cls.src("hook")

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
        proxy: bool = False,
    ):
        """
        Save the class in services options
        name: name to be used for reference
        config: config name from datasource
        manifest: manifest name from datasource
        priority: duplicate name will use the highest priority
        proxy: allow proxy service
        """

        def decorator(service: T) -> T:
            setattr(service, "__proxy__", proxy)
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
        """
        Save the class in repositories options
        name: name to be used for reference
        priority: duplicate name will use the highest priority
        """

        def decorator(repository: T) -> T:
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
    def context(cls, name: str = None, priority: int = 0):
        """
        Save the class in contexts options
        name: name to be used for reference
        priority: duplicate name will use the highest priority
        """

        def decorator(context: T) -> T:
            cls.push(
                name=name or context.__name__,
                target=cls._contexts,
                entry={
                    "type": context,
                    "priority": priority,
                    "date_added": int(datetime.utcnow().timestamp() * 1000),
                },
            )
            return context

        return decorator

    @classmethod
    def inject(cls, contexts: list = [], services: list = [], repositories: list = []):
        """
        Allow to inject instance on specific method/class
        contexts: list of context name to inject
            - can use tuple per entry (name, alias) instead of string
        services: list of service name to inject
            - can use tuple per entry (name, alias) instead of string
        repositories: list of service name to inject
            - can use tuple per entry (name, alias) instead of string
        """

        def decorator(callable):
            def argument_handler(*args, **kwargs):
                _instances = {}

                for context in contexts:
                    if isinstance(context, tuple):
                        _instances[context[1]] = cls.ctx(context[0])
                    else:
                        _instances[context] = cls.ctx(context)
                for repository in repositories:
                    if isinstance(repository, tuple):
                        _instances[repository[1]] = cls.repo(repository[0])
                    else:
                        _instances[repository] = cls.repo(repository)
                for service in services:
                    if isinstance(service, tuple):
                        _instances[service[1]] = (
                            cls.__proxy__
                            if getattr(cls.svc_cls(service[0]), "__proxy__", False)
                            and cls._use_proxy
                            else cls.svc(service[0])
                        )
                    else:
                        _instances[service] = (
                            cls.__proxy__
                            if getattr(cls.svc_cls(service), "__proxy__", False)
                            and cls._use_proxy
                            else cls.svc(service)
                        )

                kwargs.update(_instances)
                callable(*args, **kwargs)

            return argument_handler

        return decorator

    @classmethod
    def settings(cls, name: str, default=None):
        return getattr(cls._settings, name, default)
