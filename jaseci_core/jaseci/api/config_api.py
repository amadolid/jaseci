"""
Admin config api functions as a mixin
"""
from json import dumps
from jaseci.api.interface import interface


class config_api:
    """
    Admin config APIs
    Abstracted since there are no valid configs in core atm, see jaseci_serv
    to see how used.
    """

    def __init__(self, *args, **kwargs):
        self._valid_configs = [
            "CONFIG_EXAMPLE",
            "ACTION_SETS",
            "REDIS_CONFIG",
            "TASK_CONFIG",
            "EMAIL_CONFIG",
        ]

    @interface.admin_api(cli_args=["name"])
    def config_get(self, name: str, do_check: bool = True):
        """
        Get a config
        """
        if do_check and not self.name_check(name):
            return self.name_error(name)
        return self._h.get_glob(name)

    @interface.admin_api(cli_args=["name"])
    def config_set(self, name: str, value: dict or str, do_check: bool = True):
        """
        Set a config
        """
        if do_check and not self.name_check(name):
            return self.name_error(name)

        if type(value) is dict:
            value = dumps(value)

        self._h.save_glob(name, value)
        return [f"Config of '{name}' to '{value}' set!"]

    @interface.admin_api()
    def config_refresh(self, name: str):
        """
        update global configs
        """

        hook = self._h
        if name == "TASK_CONFIG":
            hook.task.reset(hook)
        elif name == "REDIS_CONFIG":
            hook.redis.reset(hook)
        elif name == "EMAIL_CONFIG":
            hook.mail.reset(hook)

    @interface.admin_api()
    def config_list(self):
        """
        Check a config is present
        """
        return [v for v in self._h.list_glob() if v in self._valid_configs]

    @interface.admin_api()
    def config_index(self):
        """
        List all valid configs
        """
        return self._valid_configs

    @interface.admin_api(cli_args=["name"])
    def config_exists(self, name: str):
        """
        Check a config is present
        """
        return self._h.has_glob(name)

    @interface.admin_api(cli_args=["name"])
    def config_delete(self, name: str, do_check: bool = True):
        """
        Delete a config
        """
        if do_check and not self.name_check(name):
            return self.name_error(name)
        self._h.destroy_glob(name)
        return [f"{name} Deleted."]

    def name_error(self, name):
        """Much used error output"""
        return [f"Config {name} not recognized, must be in {self._valid_configs}!"]

    def name_check(self, name):
        """Much used name check"""
        return name in self._valid_configs
