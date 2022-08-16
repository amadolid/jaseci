"""
This module includes code related to hooking Jaseci's django models to the
core engine.

FIX: Serious permissions work needed
"""
from django.core.exceptions import ObjectDoesNotExist

from jaseci.utils import utils
from jaseci.utils.utils import logger
import jaseci as core_mod
from jaseci.utils.mem_hook import mem_hook, json_str_to_jsci_dict
from jaseci_serv.jaseci_serv.settings import TASK_QUIET
from redis import Redis
import uuid
import json

from django_celery_results.models import TaskResult


def find_class_and_import(j_type, core_mod):
    if j_type == "master":
        from jaseci_serv.base.models import master

        return master
    elif j_type == "super_master":
        from jaseci_serv.base.models import super_master

        return super_master
    else:
        return utils.find_class_and_import(j_type, core_mod)


class orm_hook(mem_hook):
    """
    Hooks Django ORM database for Jaseci objects to Jaseci's core engine.
    """

    def __init__(self, objects, globs):
        self.objects = objects
        self.globs = globs
        super().__init__()

    def get_obj_from_store(self, item_id):
        loaded_obj = self.get_obj_from_redis(item_id)
        if not loaded_obj:
            try:
                loaded_obj = self.objects.get(jid=item_id)
            except ObjectDoesNotExist:
                logger.error(
                    str(f"Object {item_id} does not exist in Django ORM!"),
                    exc_info=True,
                )
                return None

            class_for_type = find_class_and_import(loaded_obj.j_type, core_mod)
            ret_obj = class_for_type(
                h=self, m_id=loaded_obj.j_master.urn, auto_save=False
            )
            utils.map_assignment_of_matching_fields(ret_obj, loaded_obj)
            assert uuid.UUID(ret_obj.jid) == loaded_obj.jid

            # Unwind jsci_payload for fields beyond element object
            obj_fields = json_str_to_jsci_dict(loaded_obj.jsci_obj, ret_obj)
            for i in obj_fields.keys():
                setattr(ret_obj, i, obj_fields[i])
            self.commit_obj_to_redis(ret_obj)
            return ret_obj
        return loaded_obj

    def has_obj_in_store(self, item_id):
        """
        Checks for object existance in store
        """
        return (
            self.has_obj_in_redis(item_id.urn)
            or self.objects.filter(jid=item_id).count()
        )

    def commit_obj(self, item):
        item_from_db, created = self.objects.get_or_create(jid=item.id)
        utils.map_assignment_of_matching_fields(item_from_db, item)
        item_from_db.jsci_obj = item.jsci_payload()
        item_from_db.save()

    def destroy_obj_from_store(self, item):
        self.destroy_obj_from_redis(item.id.urn)
        try:
            self.objects.get(jid=item.id).delete()
        except ObjectDoesNotExist:
            # NOTE: Should look at this at some point
            # logger.error("Object does not exists so delete aborted!")
            pass

    def get_glob_from_store(self, name):
        """
        Get global config from externally hooked general store by name
        """
        loaded_val = self.get_glob_from_redis(name)
        if not loaded_val:
            try:
                loaded_val = self.globs.get(name=name).value
            except ObjectDoesNotExist:
                logger.error(
                    str(f"Global {name} does not exist in Django ORM!"), exc_info=True
                )
                return None

            self.commit_glob_to_redis(name, loaded_val)
            return loaded_val
        return loaded_val

    def has_glob_in_store(self, name):
        """
        Checks for global config existance in store
        """
        return self.has_glob_in_redis(name) or self.globs.filter(name=name).count()

    def list_glob_from_store(self):
        """Get list of global config to externally hooked general store"""
        return [entry["name"] for entry in self.globs.values("name")]

    def destroy_glob_from_store(self, name):
        """Destroy global config to externally hooked general store"""
        self.destroy_obj_from_redis(name)
        try:
            self.globs.get(name=name).delete()
        except ObjectDoesNotExist:
            pass

    def commit_glob(self, name, value):
        self.commit_glob_to_redis(name, value)
        item_from_db, created = self.globs.get_or_create(name=name)
        item_from_db.value = value
        item_from_db.save()

    def commit(self):
        """Write through all saves to store"""
        # dist = {}
        # for i in self.save_obj_list:
        #     if (type(i).__name__ in dist.keys()):
        #         dist[type(i).__name__] += 1
        #     else:
        #         dist[type(i).__name__] = 1
        # print(dist)
        for i in self.save_obj_list:
            if not self.skip_redis_update:
                self.commit_obj_to_redis(i)
            self.commit_obj(i)
        self.save_obj_list = set()
        for i in self.save_glob_dict.keys():
            self.commit_glob(name=i, value=self.save_glob_dict[i])
        self.save_glob_dict = {}

    def celery_config(self):
        self.task_app().config_from_object("jaseci_serv.jaseci_serv.settings")
        self.task_quiet(TASK_QUIET)

    def get_by_task_id(self, task_id):
        task = self.task_app().AsyncResult(task_id)

        ret = {"status": task.state}

        if task.ready():
            task_result = TaskResult.objects.get(task_id=task_id).result
            try:
                ret["result"] = json.loads(task_result)
            except ValueError as e:
                ret["result"] = task_result

        return ret
