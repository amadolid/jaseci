import signal
from copy import deepcopy
from datetime import datetime
from typing import TypeVar, Any, Union

from .utils.utils import logger
from .jsorc_settings import JsOrcSettings
from .svc.common_svc import CommonService
from .svc.proxy_svc import ProxyService

# For future use
# from concurrent.futures import ThreadPoolExecutor
# from os import cpu_count

T = TypeVar("T")


class JsOrc:
    # ----------------- REFERENCE ----------------- #
    _contexts = {}
    _context_instances = {}

    _services = {}
    _service_instances = {}

    _repositories = {}

    # ----------------- SETTINGS ----------------- #

    _use_proxy = False
    _settings = JsOrcSettings

    # For future use
    # _executor = ThreadPoolExecutor(
    #     min(4, int((cpu_count() or 2) / 4) + 1)
    # )

    # ------------------ COMMONS ------------------ #

    _backoff_interval = 10
    __running__ = False
    __proxy__ = ProxyService()

    # ------------------- REGEN ------------------- #

    _failed_services = set()
    _regenerating = False

    @staticmethod
    def push(name: str, target: dict, entry: dict):
        if name not in target:
            target[name] = [entry]
        else:
            target[name] = sorted(
                target[name] + [entry],
                key=lambda item: (-item["priority"], -item["date_added"]),
            )

    @classmethod
    def run(cls):
        if not cls.__running__:
            cls.__running__ == True
            hook = cls.hook()
            config = hook.service_glob("JSORC_CONFIG", cls.settings("JSORC_CONFIG"))
            cls._backoff_interval = config.get("backoff_interval")

    @classmethod
    def kube(cls):
        if not cls._kube:
            raise Exception(f"Kubernetes is not yet ready!")
        return cls._kube

    #################################################
    #                    HELPER                     #
    #################################################

    # ------------------ context ------------------ #

    @classmethod
    def get(cls, context: str, cast: T = None, *args, **kwargs) -> Union[T, Any]:
        """
        Get existing context instance or build a new one that will persists
        ex: master

        context: name of the context to be build
        cast: to cast the return and allow code hinting
        *arsgs: additional argument used to initialize context
        **kwargs: additional keyword argument used to initialize context
        """
        if context not in cls._contexts:
            raise Exception(f"Context {context} is not existing!")

        if context not in cls._context_instances:
            cls._context_instances[context] = cls.ctx(context, cast, *args, **kwargs)

        return cls._context_instances[context]

    @classmethod
    def destroy(cls, context: str):
        """
        remove existing context instance
        ex: master

        context: name of the context to be build
        """
        if context not in cls._contexts:
            raise Exception(f"Context {context} is not existing!")

        if context in cls._context_instances:
            del cls._context_instances[context]

    @classmethod
    def renew(cls, context: str, cast: T = None, *args, **kwargs) -> Union[T, Any]:
        """
        renew existing context instance or build a new one that will persists
        ex: master

        context: name of the context to be build
        cast: to cast the return and allow code hinting
        *arsgs: additional argument used to initialize context
        **kwargs: additional keyword argument used to initialize context
        """
        cls.destroy(context)

        cls._context_instances[context] = cls.ctx(context, cast, *args, **kwargs)
        return cls._context_instances[context]

    @classmethod
    def ctx(cls, context: str, cast: T = None, *args, **kwargs) -> Union[T, Any]:
        """
        Build new instance of the context
        ex: master

        context: name of the context to be build
        cast: to cast the return and allow code hinting
        *arsgs: additional argument used to initialize context
        **kwargs: additional keyword argument used to initialize context
        """
        if context not in cls._contexts:
            raise Exception(f"Context {context} is not existing!")

        # highest priority
        context = cls._contexts[context][0]

        return context["type"](*args, **kwargs)

    @classmethod
    def ctx_cls(cls, context: str):
        """
        Get the context class
        """
        if context not in cls._contexts:
            return None

        return cls._contexts[context][0]["type"]

    @classmethod
    def master(cls, cast: T = None, *args, **kwargs) -> Union[T, Any]:
        """
        Generate master instance
        """
        return cls.__gen_with_hook("master", cast, *args, **kwargs)

    @classmethod
    def super_master(cls, cast: T = None, *args, **kwargs) -> Union[T, Any]:
        """
        Generate super_master instance
        """
        return cls.__gen_with_hook("super_master", cast, *args, **kwargs)

    @classmethod
    def __gen_with_hook(cls, context: str, *args, **kwargs):
        """
        Common process on master and super_master
        """
        if not kwargs.get("h", None):
            kwargs["h"] = cls.hook()

        return cls.ctx(context, None, *args, **kwargs)

    # ------------------ service ------------------ #

    @classmethod
    def _svc(cls, service: str) -> CommonService:
        if service not in cls._services:
            raise Exception(f"Service {service} is not existing!")

        # highest priority
        instance = cls._services[service][0]

        cls._use_proxy = True
        hook = cls.hook()
        cls._use_proxy = False

        config = hook.service_glob(
            instance["config"],
            cls.settings(instance["config"], cls.settings("DEFAULT_CONFIG")),
        )

        manifest = (
            hook.service_glob(
                instance["manifest"],
                cls.settings(instance["manifest"], cls.settings("DEFAULT_MANIFEST")),
            )
            if instance["manifest"]
            else {}
        )

        instance = instance["type"](config, manifest)

        if instance.has_failed() and service not in cls._failed_services:
            cls._failed_services.add(service)

        return instance

    @classmethod
    def svc(cls, service: str, cast: T = None) -> Union[T, CommonService]:
        """
        Get service. Initialize when not yet existing.
        ex: task

        service: name of the service to be reference
        cast: to cast the return and allow code hinting
        """
        if service not in cls._service_instances:
            cls._service_instances[service] = cls._svc(service)

        return cls._service_instances[service]

    @classmethod
    def svc_cls(cls, service: str):
        """
        Get the service class
        """
        if service not in cls._services:
            return None

        return cls._services[service][0]["type"]

    @classmethod
    def svc_reset(cls, service, cast: T = None) -> Union[T, CommonService]:
        """
        Service reset now deletes the actual instance and rebuild it
        """
        instance = cls._service_instances.pop(service)
        del instance
        return cls.svc(service)

    # ---------------- repository ----------------- #

    @classmethod
    def src(cls, repository: str, cast: T = None) -> Union[T, Any]:
        """
        Initialize datasource class (repository)
        ex: hook

        repository: name of the repository to be reference
        cast: to cast the return and allow code hinting
        """
        if repository not in cls._repositories:
            raise Exception(f"Repository {repository} is not existing!")

        # highest priority
        repository = cls._repositories[repository][0]

        return repository["type"]()

    @classmethod
    def hook(cls, cast: T = None) -> Union[T, Any]:
        """
        Generate hook repository instance
        """
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
                    "manifest": manifest,
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
                        _instances[repository[1]] = cls.src(repository[0])
                    else:
                        _instances[repository] = cls.src(repository)
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

    #################################################
    #                  AUTOMATION                   #
    #################################################

    @classmethod
    def regenerate(cls):
        if not cls._regenerating:
            cls._regenerating = True
            while cls._failed_services:
                failed_service = cls._failed_services.pop()
                service: CommonService = cls._service_instances[failed_service]

                if service.enabled and service.automated and service.manifest:
                    pod_name = ""
                    old_config_map = deepcopy(
                        service.manifest_meta.get("__OLD_CONFIG__", {})
                    )
                    unsafe_paraphrase = service.manifest_meta.get(
                        "__UNSAFE_PARAPHRASE__", ""
                    )
                    for kind, confs in service.manifest.items():
                        for conf in confs:
                            name = conf["metadata"]["name"]
                            names = old_config_map.get(kind, [])
                            if name in names:
                                names.remove(name)

                            if kind == "Service":
                                pod_name = name
                            res = self.read(kind, name, namespace)
                            if hasattr(res, "status") and res.status == 404 and conf:
                                self.create(kind, name, namespace, conf)
                            elif not isinstance(res, ApiException) and res.metadata:
                                if res.metadata.labels:
                                    config_version = res.metadata.labels.get(
                                        "config_version", 1
                                    )
                                else:
                                    config_version = 1

                                if config_version != conf.get("metadata").get(
                                    "labels", {}
                                ).get("config_version", 1):
                                    self.patch(kind, name, namespace, conf)

                        if (
                            old_config_map
                            and type(old_config_map) is dict
                            and kind in old_config_map
                            and name in old_config_map[kind]
                        ):
                            old_config_map.get(kind, []).remove(name)

                        for to_be_removed in old_config_map.get(kind, []):
                            res = self.read(kind, to_be_removed, namespace)
                            if not isinstance(res, ApiException) and res.metadata:
                                if (
                                    kind not in UNSAFE_KINDS
                                    or unsafe_paraphrase == UNSAFE_PARAPHRASE
                                ):
                                    self.delete(kind, to_be_removed, namespace)
                                else:
                                    logger.info(
                                        f"You don't have permission to delete `{kind}` for `{to_be_removed}` with namespace `{namespace}`!"
                                    )

                    if self.kubernetes.is_running(pod_name, namespace):
                        logger.info(
                            f"Pod state is running. Trying to Restart {svc_name}..."
                        )
                        svc.reset(hook)

            cls._regenerating = False


def interval_check(signum, frame):
    meta = MetaService()
    if meta.is_automated():
        meta.app.interval_check()
        logger.info(
            f"Backing off for {meta.app.backoff_interval} seconds before the next interval check..."
        )

        # wait interval_check to be finished before decrement
        meta.running_interval -= 1
        meta.push_interval(meta.app.backoff_interval)
    else:
        meta.running_interval -= 1


signal.signal(signal.SIGALRM, interval_check)
