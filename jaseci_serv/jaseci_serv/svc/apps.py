from django.apps import AppConfig

from jaseci import JsOrc


class CoreApiConfig(AppConfig):
    name = "jaseci_serv.svc"

    def ready(self):
        JsOrc.run()
