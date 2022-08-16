from .id_list import id_list
from .utils import logger, find_class_and_import
import jaseci as core_mod
from jaseci.task.task_hook import task_hook

import json


def json_str_to_jsci_dict(input_str, parent_obj=None):
    """
    Helper function to convert JSON strings to dictionarys with _ids list
    conversions from hex to UUID

    ret_obj is the owning object for id_list objects
    """
    try:
        obj_fields = json.loads(input_str)
    except ValueError:
        logger.error(str(f"Invalid jsci_obj string {input_str} on {parent_obj.id.urn}"))
        obj_fields = {}
    for i in obj_fields.keys():
        if str(i).endswith("_ids") and isinstance(obj_fields[i], list):
            obj_fields[i] = id_list(parent_obj=parent_obj, in_list=obj_fields[i])
    return obj_fields


class mem_hook(task_hook):
    """
    Set of virtual functions to be used as hooks to allow access to
    the complete set of items across jaseci object types. This class contains
    a number of blank function calls to be bound extrenally and passed
    to the objects. They return jaseci core types.
    """

    def __init__(self):
        from jaseci.actions.live_actions import get_global_actions

        self.mem = {"global": {}}
        self.save_obj_list = set()
        self.save_glob_dict = {}
        self.skip_redis_update = False
        self.global_action_list = get_global_actions(self)
        super().__init__()

    def get_obj(self, caller_id, item_id, override=False):
        """
        Get item from session cache by id, then try store
        TODO: May need to make this an object copy so you cant do mem writes
        """
        ret = self.get_obj_from_store(item_id)
        if override or (ret is not None and ret.check_read_access(caller_id)):
            return ret

    def has_obj(self, item_id):
        """
        Checks for object existance
        """
        return self.has_obj_in_store(item_id)

    def save_obj(self, caller_id, item, persist=False):
        """Save item to session cache, then to store"""
        if item.check_write_access(caller_id):
            self.commit_obj_to_redis(item)
            if persist:
                self.save_obj_to_store(item)

    def destroy_obj(self, caller_id, item, persist=False):
        """Destroy item from session cache then  store"""
        if item.check_write_access(caller_id):
            self.destroy_obj_from_redis(item.id.urn)
            if persist:
                self.destroy_obj_from_store(item)

    def get_glob(self, name):
        """
        Get global config from session cache by id, then try store
        """
        return self.get_glob_from_store(name)

    def has_glob(self, name):
        """
        Checks for global config existance
        """
        return self.has_glob_in_store(name)

    def resolve_glob(self, name, default=None):
        """
        Util function for returning config if exists otherwise default
        """
        if self.has_glob(name):
            return self.get_glob(name)
        else:
            return default

    def save_glob(self, name, value, persist=True):
        """Save global config to session cache, then to store"""
        self.commit_glob_to_redis(name, value)
        if persist:
            self.save_glob_to_store(name, value)

    def list_glob(self):
        """Lists all configs present"""
        glob_list = self.list_glob_from_store()
        if glob_list:
            return glob_list
        else:
            return list(self.mem["global"].keys())

    def destroy_glob(self, name, persist=True):
        """Destroy global config from session cache then store"""
        self.destroy_glob_from_redis(name)
        if persist:
            self.destroy_glob_from_store(name)

    def clear_mem_cache(self):
        """
        Clears memory, should only be used if underlying store is modified
        through other means than methods of this class
        """
        mem_hook.__init__(self)

    def has_obj_in_redis(self, key):
        if self.redis_running():
            return self.task_redis().exists(key)

        if key in self.mem.keys():
            return self.mem[key]

        return False

    def has_glob_in_redis(self, key):
        if self.redis_running():
            return self.task_redis().exists(key)

        if key in self.mem["global"].keys():
            return self.mem[key]

        return False

    def get_obj_from_redis(self, item_id):
        if self.redis_running():
            loaded_obj = self.task_redis().get(item_id.urn)
            if loaded_obj:
                jdict = json.loads(loaded_obj)
                j_type = jdict["j_type"]
                j_master = jdict["j_master"]
                class_for_type = find_class_and_import(j_type, core_mod)
                ret_obj = class_for_type(h=self, m_id=j_master, auto_save=False)
                ret_obj.json_load(loaded_obj)
                return ret_obj

        elif item_id in self.mem:
            return self.mem[item_id]

        return None

    def get_glob_from_redis(self, name):

        if self.redis_running():
            return self.task_redis().get(name)

        elif name in self.mem["global"]:
            return self.mem["global"][name]

        return None

    def commit_glob_to_redis(self, name, value):
        if self.redis_running():
            self.task_redis().set(name, value)
        else:
            self.mem["global"][name] = value

    def commit_obj_to_redis(self, item):
        if self.redis_running():
            self.task_redis().set(item.id.urn, item.json(detailed=True))
        else:
            self.mem[item.id.urn] = item

    def destroy_glob_from_redis(self, name):
        if self.redis_running():
            self.task_redis().delete(name)
        elif name in self.mem["global"]:
            self.mem["global"].pop(name)

    def destroy_obj_from_redis(self, name):

        if name in self.save_obj_list:
            self.save_obj_list.remove(name)

        if name in self.save_glob_dict.keys():
            self.save_glob_dict.pop(name)

        if self.redis_running():
            self.task_redis().delete(name)
        elif name in self.mem:
            self.mem.pop(name)

    def get_obj_from_store(self, item_id):
        """
        Get item from externally hooked general store by id
        """
        return self.get_obj_from_redis(item_id)

    def has_obj_in_store(self, item_id):
        """
        Checks for object existance in store
        """
        return self.has_obj_in_redis(item_id.urn)

    def save_obj_to_store(self, item):
        # import traceback as tb; tb.print_stack();  # noqa
        self.save_obj_list.add(item)

    def destroy_obj_from_store(self, item):
        """Destroy item to externally hooked general store"""
        self.destroy_obj_from_redis(item.id.urn)

    def get_glob_from_store(self, name):
        """
        Get global config from externally hooked general store by name
        """
        return self.get_glob_from_redis(name)

    def has_glob_in_store(self, name):
        """
        Checks for global config existance in store
        """
        return self.has_glob_in_redis(name)

    def save_glob_to_store(self, name, value):
        """Save global config to externally hooked general store"""
        self.save_glob_dict[name] = value

    def list_glob_from_store(self):
        """Get list of global config to externally hooked general store"""
        if self.redis_running():
            logger.warning("Globals can not (yet) be listed from Redis!")
            return []
        else:
            return list(self.mem["global"].keys())

    def destroy_glob_from_store(self, name):
        """Destroy global config to externally hooked general store"""
        self.destroy_obj_from_redis(name)

    def commit(self):
        if self.redis_running():
            if not self.skip_redis_update:
                for i in self.save_obj_list:
                    self.commit_obj_to_redis(i)

            for i in self.save_glob_dict.keys():
                self.commit_glob_to_redis(name=i, value=self.save_glob_dict[i])

        self.save_obj_list = set()
        self.save_glob_dict = {}

    # Utilities
    def get_object_distribution(self):
        dist = {}
        for i in self.mem.keys():
            t = type(self.mem[i])
            if t in dist.keys():
                dist[t] += 1
            else:
                dist[t] = 1
        return dist
