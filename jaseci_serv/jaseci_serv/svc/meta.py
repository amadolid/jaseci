from jaseci.svc import MetaService as Ms, PrometheusService
from .config import RUN_SVCS


class MetaService(Ms):
    ###################################################
    #                   OVERRIDEN                     #
    ###################################################
    def __init__(self):
        super().__init__(run_svcs=RUN_SVCS)

    ###################################################
    #                   OVERRIDEN                     #
    ###################################################

    def populate_context(self):
        from jaseci_serv.hook.orm import OrmHook
        from jaseci_serv.base.models import (
            Master,
            SuperMaster,
        )

        self.add_context("hook", OrmHook)
        self.add_context("master", Master)
        self.add_context("super_master", SuperMaster)

    def populate_services(self):
        self.add_service_builder("promon", PrometheusService)
