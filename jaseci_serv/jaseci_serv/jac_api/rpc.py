from modernrpc.core import rpc_method, REQUEST_KEY

from jaseci_serv.base.orm_hook import orm_hook
from jaseci_serv.base.models import JaseciObject, GlobalVars
from jaseci_serv.base.models import master as core_master


@rpc_method(entry_point="private")
def walker(api, body, **kwargs):
    caller = kwargs[REQUEST_KEY].user.get_master()
    return caller.general_interface_to_api(body, api)


@rpc_method(entry_point="public")
def public_walker(api, body):
    caller = core_master(
        h=orm_hook(objects=JaseciObject.objects, globs=GlobalVars.objects),
        persist=False,
    )
    return caller.public_interface_to_api(body, api)
