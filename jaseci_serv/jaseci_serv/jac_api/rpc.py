from modernrpc.core import rpc_method
from knox.models import AuthToken
from knox.settings import CONSTANTS

from django.utils import timezone

from jaseci_serv.base.orm_hook import orm_hook
from jaseci_serv.base.models import JaseciObject, GlobalVars
from jaseci_serv.base.models import master as core_master


@rpc_method(entry_point="private")
def walker(token, api, body):
    try:
        return (
            AuthToken.objects.get(
                token_key=token[: CONSTANTS.TOKEN_KEY_LENGTH],
                expiry__gte=timezone.now(),
            )
            .user.get_master()
            .general_interface_to_api(body, api)
        )
    except AuthToken.DoesNotExist as e:
        return {"err_msg": "Forbidden Request!"}


@rpc_method(entry_point="public")
def public_walker(api, body):
    caller = core_master(
        h=orm_hook(objects=JaseciObject.objects, globs=GlobalVars.objects),
        persist=False,
    )
    return caller.public_interface_to_api(body, api)
