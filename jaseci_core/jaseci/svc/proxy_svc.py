from .state import ServiceState as Ss
from jaseci.svc.common_svc import CommonService


class ProxyService(CommonService):
    def __init__(self):
        self.app = None
        self.state = Ss.NOT_STARTED
        self.enabled = False
        self.quiet = False
