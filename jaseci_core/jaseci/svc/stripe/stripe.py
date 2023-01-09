import stripe
from jaseci.svc import CommonService
from .config import STRIPE_CONFIG

#################################################
#                  STRIPE APP                   #
#################################################


class StripeService(CommonService):

    ###################################################
    #                     BUILDER                     #
    ###################################################

    def run(self, hook=None):
        if not self.config.get("api_key"):
            raise Exception("api_key is required!")

        self.app = stripe
        self.app.api_key = self.config.get("api_key")
        self.walker = self.config.get("walker")

    ####################################################
    #                    OVERRIDDEN                    #
    ####################################################

    def reset(self, hook, start=True):
        stripe.api_key = None
        super().reset(hook, start)

    def build_config(self, hook) -> dict:
        return hook.service_glob("STRIPE_CONFIG", STRIPE_CONFIG)
