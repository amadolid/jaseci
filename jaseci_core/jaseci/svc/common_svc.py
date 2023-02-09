from .state import ServiceState as Ss
from jaseci.utils.utils import logger
from multiprocessing import Process


class CommonService:

    ###################################################
    #                   PROPERTIES                    #
    ###################################################

    # ------------------- DAEMON -------------------- #

    _daemon = {}

    @property
    def daemon(self):
        return __class__._daemon

    def __init__(self, config: dict, manifest: dict):
        self.app = None
        self.state = Ss.NOT_STARTED

        # ------------------- CONFIG -------------------- #

        self.config = config
        self.enabled = config.pop("enabled", False)
        self.quiet = config.pop("quiet", False)

        # ------------------ MANIFEST ------------------- #

        self.manifest = manifest
        self.manifest_meta = {
            "__OLD_CONFIG__": manifest.pop("__OLD_CONFIG__", {}),
            "__UNSAFE_PARAPHRASE__": manifest.pop("__UNSAFE_PARAPHRASE__", ""),
        }

        self.start()

    ###################################################
    #                     BUILDER                     #
    ###################################################

    def start(self):
        try:
            if self.enabled and self.is_ready():
                self.state = Ss.STARTED
                self.run()
                self.state = Ss.RUNNING
                self.post_run()
        except Exception as e:
            if not (self.quiet):
                logger.error(
                    f"Skipping {self.__class__.__name__} due to initialization "
                    f"failure!\n{e.__class__.__name__}: {e}"
                )
            self.failed()

        return self

    def run(self):
        raise Exception(f"Not properly configured! Please override run method!")

    def post_run(self):
        pass

    # ------------------- DAEMON -------------------- #

    def spawn_daemon(self, **targets):
        for name, target in targets.items():
            dae: Process = self.daemon.get(name)
            if not dae or not dae.is_alive():
                process = Process(target=target, daemon=True)
                process.start()
                self.daemon[name] = process

    def terminate_daemon(self, *names):
        for name in names:
            dae: Process = self.daemon.pop(name, None)
            if not (dae is None) and dae.is_alive():
                logger.info(f"Terminating {name} ...")
                dae.terminate()

    ###################################################
    #                     COMMONS                     #
    ###################################################

    def poke(self, msg: str = None):
        if self.is_running():
            return self.app
        raise Exception(
            msg or f"{self.__class__.__name__} is disabled or not yet configured!"
        )

    def is_ready(self):
        return self.state.is_ready() and self.app is None

    def is_running(self):
        return self.state.is_running() and not (self.app is None)

    def has_failed(self):
        return self.state.has_failed()

    def failed(self):
        self.app = None
        self.state = Ss.FAILED

    # ---------------- PROXY EVENTS ----------------- #

    def on_delete(self):
        pass

    # ------------------- EVENTS -------------------- #

    def __del__(self):
        self.on_delete()
