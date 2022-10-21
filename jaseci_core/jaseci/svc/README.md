# HOW TO USE SERVICE

## `CommonService` (jaseci.svc.common)
This class is the base for implementing service. Dev should use this class if they want to use Service's common attribute and life cycle.

---

## `Common Attributes`

| Attribute | Description |
| ----------- | ----------- |
| app | Attribute for the actual library used in service. For example in TaskService is Celery |
| enabled | If service is enabled in config. The service can be available (upon building) but not enabled (from config) |
| state | For `service life cycle` |
| quiet | For log control and avoid uncessary logs |

---

## `Common Methods`
| Methods | Arguments | Description | Example |
| ----------- | ----------- | ----------- | ----------- |
| `start` | `hook`=nullable | start the actual service based on settings (`kube,config`) | `RedisService().start()` |
| `is_ready` | | check if state is `NOT_STARTED` and app is not yet set | |
| `is_running` | | check if state is `RUNNING` and app is set | |
| `has_failed` | | check if state is `FAILED` | |
| `spawn_daemon` | name_of_daemon=targe_method | spawn daemon threads for background process | `self.spawn_daemon(jsorc=self.interval_check)` |
| `terminate_daemon` | name_of_daemon_to_terminate... | terminate daemon threads | `self.terminate_daemon("jsorc", "other_daemon_name")` |

---

## `Service Life Cycle` (can be overriden)
- `__init__` (initial trigger for `build_service`)
    - this is optional to be overriden if you have additional fields to be use
    - initial state would be `NOT_STARTED`
```python
    def __init__(self, hook=None):
        super().__init__(hook) # run CommonService init
        # ... your other code here ...
```

- `build_kube` (required to be overriden if you have kube settings)
    - will be called upon build and before `build_config`
    - sample kube config are on `jaseci_serv.jaseci_serv.kubes`
```python
    def build_kube(self, hook) -> dict:
        return hook.service_glob("REDIS_KUBE", REDIS_KUBE) # common implementation using global vars
```

- `build_config` (required to be overriden)
    - will be called upon build and after `build_kube`
    - sample config are on `jaseci_serv.jaseci_serv.configs`
```python
    def build_config(self, hook) -> dict:
        return hook.service_glob("REDIS_CONFIG", REDIS_CONFIG) # common implementation using global vars
```

- `run` (required to be overriden)
    - triggered upon `service.start()`
    - upon trigger `start` it still need to check if it's enabled and on ready state (`NOT_STARTED`)
    - if service is not enabled this method will be ignored
    - if service is enabled but state is not equal to `NOT_STARTED` run method will also be ignored
    - if all requirements were met, state will be updated to `STARTED` before running run method
    - if run method raised some exception, state will update to `FAILED` and `failed` method will be called
    - if run method is executed without error state will be updated to `RUNNING`

```python
    def run(self, hook=None):
        self.__convert_config(hook)
        self.app = self.connect() # connect will return Mailer class with stmplib.SMTP (mail.py example)
```

- `post_run` (optional)
    - triggered after `run` method and if state is already set to `RUNNING`

```python
   def post_run(self, hook=None):
        self.spawn_daemon(
            worker=self.app.Worker(quiet=self.quiet).start,
            scheduler=self.app.Beat(socket_timeout=None, quiet=self.quiet).run,
        ) # spawn some threads for Celery worker and scheduler
```

- `failed` (optional)
    - this will be used if you have other process that needs to be executed upon start failure
```python
    def failed(self):
        super().failed()
        self.terminate_daemon("worker", "scheduler") # close some thread when error occurs (task.py example)
```

- `reset` (optional)
    - this will be used if you have other process that needs to be executed upon resetting
```python
    def reset(self, hook):
        if self.is_running():
            self.app.terminate() # app needs to be terminated before calling the actual reset

        super().reset(hook)
```




