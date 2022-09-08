from jaseci.app.common_app import hook_app as ha


class hook_app(ha):
    def build_hook(self):
        from jaseci_serv.base.models import GlobalVars, JaseciObject
        from jaseci_serv.base.orm_hook import orm_hook

        return orm_hook(objects=JaseciObject.objects, globs=GlobalVars.objects)
