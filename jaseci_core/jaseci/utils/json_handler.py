from json import JSONDecoder, JSONEncoder
from uuid import UUID


class JaseciJsonEncoder(JSONEncoder):
    def default(self, obj):
        from jaseci.element.element import element

        if isinstance(obj, element):
            return {"__mem_id__": obj.id.urn}
        else:
            return super().default(obj)


class JaseciJsonDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if isinstance(obj, dict):
            if "__mem_id__" in obj:
                return self.convert(obj["__mem_id__"])
            else:
                for k in obj:
                    self.transform(obj, k)
        elif isinstance(obj, (list, tuple)):
            for idx, k in enumerate(obj):
                self.transform(obj, idx)
        return obj

    def transform(self, obj, key):
        if isinstance(obj[key], dict):
            if "__mem_id__" in obj[key]:
                obj[key] = self.convert(obj[key]["__mem_id__"])
            else:
                for k in obj[key]:
                    self.transform(obj[key], k)
        elif isinstance(obj[key], (list, tuple)):
            for idx, k in enumerate(obj[key]):
                self.transform(obj[key], idx)

    def convert(self, urn):
        from jaseci.task.task_hook import task_hook

        return task_hook.main_hook.get_obj_from_store(UUID(urn))
