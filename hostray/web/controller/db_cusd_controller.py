# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Tuesday, 5th November 2019 by hsky77 (howardlkung@gmail.com)
'''


from typing import Dict

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from hostray.util.orm import EntityBaseAddon, OrmDBEntityAccessor

from .. import (HostrayWebException,
                LocalCode_Not_Accessor_Function,
                LocalCode_Cache_Expired,
                LocalCode_Data_Added,
                LocalCode_Data_Updated,
                LocalCode_Data_Delete,
                LocalCode_Data_No_Changed,
                LocalCode_Data_Not_Exist,
                LocalCode_Data_Added_Failed)
from ..component import OptionalComponentTypes
from ..component.optional_component import OrmDBComponent

from .. import HostrayWebFinish
from .request_controller import RequestController, RESTfulMethodType


class DBCSUDController(RequestController):
    qn_key = 'queried_entities'

    orm_db_accessor: OrmDBEntityAccessor = None
    orm_db_methods: dict = {k.value: None for k in RESTfulMethodType}

    def initialize(self, use_orm_db):
        self.orm_db: OrmDBComponent = self.application.component_manager.get_component(
            OptionalComponentTypes.OrmDB)

        self.db_id = use_orm_db
        self.orm_db.init_db_declarative_base(
            self.db_id, self.orm_db_accessor.entity_cls)

        self.orm_db_methods = {
            RESTfulMethodType.GET.value: self.orm_db_methods[RESTfulMethodType.GET.value] or self.orm_db_accessor.select,
            RESTfulMethodType.POST.value: self.orm_db_methods[RESTfulMethodType.POST.value] or self.orm_db_accessor.add,
            RESTfulMethodType.PUT.value: self.orm_db_methods[RESTfulMethodType.PUT.value] or self.orm_db_accessor.merge,
            RESTfulMethodType.DELETE.value: self.orm_db_methods[RESTfulMethodType.DELETE.value] or self.orm_db_accessor.delete,
            RESTfulMethodType.PATCH.value: self.orm_db_methods[
                RESTfulMethodType.PATCH.value] or self.orm_db_accessor.set_attribute
        }

        self.required_arugments = {
            k.value: self.orm_db_accessor.entity_cls.primary_keys() for k in [
                RESTfulMethodType.POST, RESTfulMethodType.PATCH, RESTfulMethodType.DELETE]
        }

    def get_orm_db_method(self):
        if not callable(self.orm_db_methods[self.request.method]):
            raise HostrayWebException(LocalCode_Not_Accessor_Function)
        return self.orm_db_methods[self.request.method]

    async def get(self):
        keys = self.get_allowed_arguments()
        await self.orm_db.reset_session_async(self.db_id)
        async with self.orm_db.reserve_worker_async(self.db_id) as identity:
            entities = await self.orm_db.run_accessor_async(self.db_id, self.get_orm_db_method(), identity=identity, **keys)

            if entities is not None:
                entities = entities if isinstance(
                    entities, list) else [entities]
                for entity in entities:
                    self._update_entity_cache(entity)
                    self.write(entity.to_client_dict())

    async def post(self):
        keys = self.get_allowed_arguments()
        rkeys = self.get_required_valid_arguments()
        async with self.orm_db.reserve_worker_async(self.db_id) as identity:
            try:
                entity: EntityBaseAddon = await self.orm_db.run_accessor_async(self.db_id, self.get_orm_db_method(), identity=identity, **keys)

                changed = await self.orm_db.run_accessor_async(self.db_id, self.orm_db_accessor.save, identity=identity)
                entity = await self.orm_db.run_accessor_async(self.db_id, self.orm_db_accessor.refresh, entity, identity=identity)
                self.changed_data = entity.to_dict()
                self._update_entity_cache(entity)

                if changed[0] > 0:  # new row count
                    self.write(self.get_localized_message(
                        LocalCode_Data_Added))
                else:
                    self.write(self.get_localized_message(
                        LocalCode_Data_No_Changed))

                await self.orm_db.reset_session_async(self.db_id, force_reconnect=True)
            except IntegrityError:
                await self.orm_db.run_accessor_async(self.db_id, self.orm_db_accessor.rollback, identity=identity)
                raise HostrayWebFinish(LocalCode_Data_Added_Failed)
            except:
                await self.orm_db.run_accessor_async(self.db_id, self.orm_db_accessor.rollback, identity=identity)
                raise

    async def put(self):
        keys = self.get_allowed_arguments()
        async with self.orm_db.reserve_worker_async(self.db_id) as identity:
            try:
                entity: EntityBaseAddon = await self.orm_db.run_accessor_async(self.db_id, self.get_orm_db_method(), identity=identity, **keys)

                changed = await self.orm_db.run_accessor_async(self.db_id, self.orm_db_accessor.save, identity=identity)
                entity = await self.orm_db.run_accessor_async(self.db_id, self.orm_db_accessor.refresh, entity, identity=identity)
                self.changed_data = entity.to_dict()
                self._update_entity_cache(entity)

                if entity is not None:
                    self.write(self.get_localized_message(
                        LocalCode_Data_Added))
                else:
                    self.write(self.get_localized_message(
                        LocalCode_Data_No_Changed))

                await self.orm_db.reset_session_async(self.db_id, force_reconnect=True)
            except:
                await self.orm_db.run_accessor_async(self.db_id, self.orm_db_accessor.rollback, identity=identity)
                raise

    async def delete(self):
        self._check_entity_cache()
        rkeys = self.get_required_valid_arguments()

        async with self.orm_db.reserve_worker_async(self.db_id) as identity:
            try:
                entity = await self.orm_db.run_accessor_async(self.db_id, self.orm_db_accessor.load, identity=identity, **rkeys)
                if entity is None:
                    raise HostrayWebFinish(LocalCode_Data_Not_Exist)

                self._check_entity_cache(entity)
                self.changed_data = entity.to_dict()
                entity_identity = entity.identity
                entity_type = type(entity)
                await self.orm_db.run_accessor_async(self.db_id, self.get_orm_db_method(), entity, identity=identity)
                _, _, delete = await self.orm_db.run_accessor_async(self.db_id, self.orm_db_accessor.save, identity=identity)

                if delete > 0:
                    self._delete_entity_cache(entity_type, entity_identity)
                    self.write(self.get_localized_message(
                        LocalCode_Data_Delete))
                else:
                    self.write(self.get_localized_message(
                        LocalCode_Data_No_Changed))

                await self.orm_db.reset_session_async(self.db_id, force_reconnect=True)
            except:
                await self.orm_db.run_accessor_async(self.db_id, self.orm_db_accessor.rollback, identity=identity)
                raise

    async def patch(self):
        self._check_entity_cache()
        rkeys = self.get_required_valid_arguments()
        akeys = self.get_allowed_arguments()
        params = self.get_non_required_valid_arguments()

        async with self.orm_db.reserve_worker_async(self.db_id) as identity:
            try:
                entity = await self.orm_db.run_accessor_async(self.db_id, self.orm_db_accessor.load, identity=identity, **rkeys)

                if entity is None:
                    raise HostrayWebFinish(LocalCode_Data_Not_Exist)
                self._check_entity_cache(entity)

                await self.orm_db.run_accessor_async(self.db_id, self.get_orm_db_method(), entity, identity=identity, **params)
                _, update, _ = await self.orm_db.run_accessor_async(self.db_id, self.orm_db_accessor.save, identity=identity)
                entity = await self.orm_db.run_accessor_async(self.db_id, self.orm_db_accessor.refresh, entity, identity=identity)
                self.changed_data = entity.to_dict()
                self._update_entity_cache(entity)

                await self.orm_db.reset_session_async(self.db_id, force_reconnect=True)
                if update > 0:
                    self.write(self.get_localized_message(
                        LocalCode_Data_Updated))
                else:
                    self.write(self.get_localized_message(
                        LocalCode_Data_No_Changed))
            except:
                await self.orm_db.run_accessor_async(self.db_id, self.orm_db_accessor.rollback, identity=identity)
                raise

    def _check_entity_cache(self, entity: EntityBaseAddon = None) -> bool:
        if self.cache is not None:
            if not self.qn_key in self.cache:
                raise HostrayWebFinish(LocalCode_Cache_Expired)

            if entity is not None:
                if type(entity) in self.cache[self.qn_key]:
                    if entity.identity in self.cache[self.qn_key][type(entity)]:
                        if not self._copy_equals(entity.to_dict(), self.cache[self.qn_key][type(entity)][entity.identity]):
                            raise HostrayWebFinish(
                                LocalCode_Cache_Expired)
                    else:
                        raise HostrayWebFinish(
                            LocalCode_Cache_Expired)
                else:
                    raise HostrayWebFinish(LocalCode_Cache_Expired)

    def _delete_entity_cache(self, entity: EntityBaseAddon, identity):
        if self.cache is not None:
            if self.qn_key in self.cache:
                if type(entity) in self.cache[self.qn_key]:
                    self.cache[self.qn_key][type(entity)].pop(identity)

    def _update_entity_cache(self, entity: EntityBaseAddon):
        if self.cache is not None:
            if not self.qn_key in self.cache:
                self.cache[self.qn_key] = {}

            identity_key = type(entity)
            if not identity_key in self.cache[self.qn_key]:
                self.cache[self.qn_key][identity_key] = {}

            identity = entity.identity
            self.cache[self.qn_key][identity_key][identity] = entity.to_dict()

    def _copy_equals(self, l: Dict, r: Dict) -> bool:
        for k, v in l.items():
            if not r[k] == v:
                return False
        return True
