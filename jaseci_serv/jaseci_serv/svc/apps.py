from django.apps import AppConfig


class CoreApiConfig(AppConfig):
    name = "jaseci_serv.svc"

    def ready(self):
        print("####################")
        print(2)
        print("####################")
