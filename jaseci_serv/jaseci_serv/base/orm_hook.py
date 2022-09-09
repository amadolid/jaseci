"""
This module includes code related to hooking Jaseci's django models to the
core engine.

FIX: Serious permissions work needed
"""
from django.core.exceptions import ObjectDoesNotExist
from jaseci.app.redis.redis_app import redis_app

from jaseci.utils import utils

from jaseci.utils.redis_hook import redis_hook
from jaseci.utils.utils import logger
from jaseci.utils.json_handler import json_str_to_jsci_dict
import jaseci as core_mod
from jaseci_serv.app.common_app import meta_app
from jaseci_serv.app.task.task_app import task_app
import uuid

from jaseci_serv.jaseci_serv.settings import ALLOW_APPS


class orm_hook(redis_hook):
    """
    Hooks Django ORM database for Jaseci objects to Jaseci's core engine.
    """

    def __init__(self, objects, globs):
        self.objects = objects
        self.globs = globs
        super().__init__(ALLOW_APPS)

    ####################################################
    #                       APPS                       #
    ####################################################

    def __meta__(self):
        self._meta = meta_app()

    def build_apps(self):
        self.redis = redis_app(self)
        self.task = task_app(self)

    ####################################################
    #                DATASOURCE METHOD                 #
    ####################################################

    # --------------------- OBJ ---------------------- #

    def get_obj_from_store(self, item_id):
        loaded_obj = super().get_obj_from_store(item_id)
        if loaded_obj is None:
            try:
                loaded_obj = self.objects.get(jid=item_id)
            except ObjectDoesNotExist:
                logger.error(
                    str(f"Object {item_id} does not exist in Django ORM!"),
                    exc_info=True,
                )
                return None

            class_for_type = self.find_class_and_import(loaded_obj.j_type, core_mod)
            ret_obj = class_for_type(
                h=self, m_id=loaded_obj.j_master.urn, auto_save=False
            )
            utils.map_assignment_of_matching_fields(ret_obj, loaded_obj)
            assert uuid.UUID(ret_obj.jid) == loaded_obj.jid

            # Unwind jsci_payload for fields beyond element object
            obj_fields = json_str_to_jsci_dict(loaded_obj.jsci_obj, ret_obj)
            for i in obj_fields.keys():
                setattr(ret_obj, i, obj_fields[i])
            self.commit_obj_to_cache(ret_obj)
            return ret_obj
        return loaded_obj

    def has_obj_in_store(self, item_id):
        """
        Checks for object existance in store
        """
        return super().has_obj_in_store(item_id) or (
            self.objects.filter(jid=item_id).count()
        )

    def destroy_obj_from_store(self, item):
        super().destroy_obj_from_store(item)
        try:
            self.objects.get(jid=item.id).delete()
        except ObjectDoesNotExist:
            # NOTE: Should look at this at some point
            # logger.error("Object does not exists so delete aborted!")
            pass

    # --------------------- GLOB --------------------- #

    def get_glob_from_store(self, name):
        """
        Get global config from externally hooked general store by name
        """

        glob = super().get_glob_from_store(name)
        if glob is None:
            try:
                glob = self.globs.get(name=name).value
            except ObjectDoesNotExist:
                logger.error(
                    str(f"Global {name} does not exist in Django ORM!"), exc_info=True
                )
                return None

            super().commit_glob_to_cache(name, glob)
            return glob
        return glob

    def has_glob_in_store(self, name):
        """
        Checks for global config existance in store
        """
        return super().has_glob_in_store(name) or self.globs.filter(name=name).count()

    def list_glob_from_store(self):
        """Get list of global config to externally hooked general store"""
        globs = super().list_glob_from_store()

        if not globs:
            return [entry["name"] for entry in self.globs.values("name")]

        return globs

    def destroy_glob_from_store(self, name):
        """Destroy global config to externally hooked general store"""
        super().destroy_glob_from_store(name)
        try:
            self.globs.get(name=name).delete()
        except ObjectDoesNotExist:
            pass

    ####################################################
    #                    COMMITTER                     #
    ####################################################

    def commit_obj(self, item):
        self.commit_obj_to_cache(item)
        item_from_db, created = self.objects.get_or_create(jid=item.id)
        utils.map_assignment_of_matching_fields(item_from_db, item)
        item_from_db.jsci_obj = item.jsci_payload()
        item_from_db.save()

    def commit_glob(self, name, value):
        self.commit_glob_to_cache(name, value)
        item_from_db, created = self.globs.get_or_create(name=name)
        item_from_db.value = value
        item_from_db.save()

    def commit(self):
        """Write through all saves to store"""
        for i in self.save_obj_list:
            self.commit_obj(i)
        self.save_obj_list = set()

        for k, v in self.save_glob_dict.items():
            self.commit_glob(k, v)
        self.save_glob_dict = {}

    ###################################################
    #                  CLASS CONTROL                  #
    ###################################################

    def find_class_and_import(self, j_type, core_mod):
        if j_type == "master":
            from jaseci_serv.base.models import master

            return master
        elif j_type == "super_master":
            from jaseci_serv.base.models import super_master

            return super_master
        else:
            return utils.find_class_and_import(j_type, core_mod)
