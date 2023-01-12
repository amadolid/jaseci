from jaseci.svc import CommonService
from .config import ELASTIC_CONFIG
from requests import get, post


#################################################
#                  ELASTIC APP                  #
#################################################


class ElasticService(CommonService):

    ###################################################
    #                     BUILDER                     #
    ###################################################

    def run(self, hook=None):
        self.app = Elastic(self.config)

    ####################################################
    #                    OVERRIDDEN                    #
    ####################################################

    def build_config(self, hook) -> dict:
        return hook.service_glob("ELASTIC_CONFIG", ELASTIC_CONFIG)


class Elastic:
    def __init__(self, config):
        self.url = config["url"]
        self.headers = {
            "Authorization": config["auth"],
            "Content-Type": "application/json",
        }
        self.common_index = config["common_index"]
        self.activity_index = config["activity_index"]

    def _get(self, url: str, json: dict):
        return get(f"{self.url}/{url}", json=json, headers=self.headers).json()

    def _post(self, url: str, json: dict):
        return post(f"{self.url}/{url}", json=json, headers=self.headers).json()

    def post(self, url: str, body: dict, index: str, suffix: str = ""):
        return self._post(f"{index or self.common_index}{suffix}{url}", body)

    def post_act(self, url: str, body: dict, suffix: str = ""):
        return self.post(url, body, self.activity_index, suffix)

    def get(self, url: str, body: dict, index: str, suffix: str = ""):
        return self._get(f"{index or self.common_index}{suffix}{url}", body)

    def get_act(self, url: str, body: dict, suffix: str = ""):
        return self.get(url, body, self.activity_index, suffix)

    def doc(self, log: dict, query: str, index: str, suffix: str = ""):
        return self.post(f"/_doc?{query}", log, index, suffix)

    def doc_activity(self, log: dict, query: str, suffix: str = ""):
        return self.doc(log, query, self.activity_index, suffix)

    def search(self, body: dict, query: str, index: str, suffix: str = ""):
        return self.get(f"/_search?{query}", body, index, suffix)

    def search_activity(self, body: dict, query: str, suffix: str = ""):
        return self.search(body, query, self.activity_index, suffix)

    def mapping(self, query: str, index: str, suffix: str = ""):
        return self.get(f"/_mapping?{query}", index, suffix)

    def mapping_activity(self, query: str, suffix: str = ""):
        return self.mapping(query, self.activity_index, suffix)

    def aliases(self, query: str = "pretty=true"):
        return self._get(f"/_aliases?{query}")

    def reindex(self, body: dict, query: str = "pretty"):
        return self._post(f"/_reindex?{query}", body)
