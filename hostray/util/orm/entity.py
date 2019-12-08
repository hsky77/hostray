# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Monday, 4th November 2019 by hsky77 (howardlkung@gmail.com)
'''


from enum import Enum
from datetime import datetime
from typing import Dict, Any, Tuple, List, Union

from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

from .. import (PY_DT_Converter, str_to_datetime, LocalizedMessageWarning,
                LocalCode_Not_Allow_Update, LocalCode_Must_Be_Type, LocalCode_Invalid_Column)


DeclarativeBases: dict = {}


def get_declarative_base(key: str = 'default') -> DeclarativeMeta:
    """
    get entity class declarative meta class
    """
    if not key in DeclarativeBases:
        DeclarativeBases[key] = declarative_base()
    return DeclarativeBases[key]


Entity = DeclarativeMeta


class EntityBaseAddon():
    """
    helper functions for:
        - entity column type validation
        - fix column value after inserting data
        - excluding entity column for responding entity data to client
    """

    # indicate the column type for validation
    column_type_validations: Dict[str, Any] = {}

    # indicate the columns are not allowed to update value
    column_fix = []

    # indicate the excluded columns for the entity data should be response to client
    client_excluded_columns = []

    # indicate datetime converter from database to json serializable dict
    dt_converter = PY_DT_Converter

    @property
    def identity(self) -> Tuple[Any]:
        """get identity of this entity, this is usually tuple of primary key columns' data"""
        return self._sa_instance_state.identity

    @property
    def primary_key_args(self) -> Dict[str, Any]:
        """get dict contains primary key columns"""
        return {k: v for k, v in self.to_dict().items() if (
            k in [x.name for x in inspect(type(self)).primary_key])}

    @property
    def non_primary_key_args(self) -> Dict[str, Any]:
        """get dict contains non-primary key columns"""
        return {k: v for k, v in self.to_dict().items() if (
            k not in [x.name for x in inspect(type(self)).primary_key])}

    @classmethod
    def primary_keys(cls) -> List[str]:
        """get list of primary key column names"""
        return [x.name for x in inspect(cls).primary_key]

    @classmethod
    def non_primary_keys(cls) -> List[str]:
        """get list of non-primary key column names"""
        pkeys = cls.primary_keys()
        return [x.name for x in inspect(cls).columns if not x.name in pkeys]

    @classmethod
    def columns(cls) -> List[str]:
        """get list of column names"""
        return [x.name for x in inspect(cls).columns]

    @classmethod
    def get_primary_key_args(cls, **kwargs) -> Dict[str, Any]:
        """get dict contains primary key column args by filtering kwargs"""
        pkeys = cls.primary_keys()
        return {k: v for k, v in kwargs.items() if k in pkeys}

    @classmethod
    def get_non_primary_key_args(cls, **kwargs) -> Dict[str, Any]:
        """get dict contains non-primary key column args by filtering kwargs"""
        pkeys = cls.non_primary_keys()
        return {k: v for k, v in kwargs.items() if k in pkeys}

    @classmethod
    def get_entity_args(cls, **kwargs) -> Dict[str, Any]:
        """get dict contains non-primary key column args by filtering kwargs"""
        columns = cls.columns()
        return {k: v for k, v in kwargs.items() if k in columns}

    @classmethod
    def get_non_entity_args(cls, **kwargs) -> Dict[str, Any]:
        """get dict contains non-entity-column args by filtering kwargs"""
        columns = cls.columns()
        return {k: v for k, v in kwargs.items() if not k in columns}

    def parameter_validation(self, check_fix: bool = True, **kwargs) -> None:
        """
        this function should be called when inserting or updating the db entity,
        usually set check_fix to False when inserting db entity
        """
        for column, value in kwargs.items():
            if column in self.column_type_validations:
                try:
                    self.column_type_validations[column](value)
                except:
                    raise LocalizedMessageWarning(
                        LocalCode_Must_Be_Type, column, self.column_type_validations[column].__name__)

            if check_fix:
                if column in self.column_fix:
                    raise LocalizedMessageWarning(
                        LocalCode_Not_Allow_Update, column)

    def to_client_dict(self) -> Dict[str, Any]:
        """return json serializable dict for the response to client"""
        return {k: v for k, v in self.to_dict().items() if not k in self.client_excluded_columns}

    def to_dict(self) -> Dict[str, Any]:
        """return json serializable dict"""
        d = self.__dict__.copy()
        d.pop('_sa_instance_state')

        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = self.dt_converter.dt_to_str(v)
        return d

    def equals(self, r: Entity) -> bool:
        """compare entity data with r"""
        if isinstance(r, EntityBaseAddon):
            r = r.to_dict()
            for k, v in self.to_dict().items():
                if not r[k] == v:
                    return False
            return True
        return False


Entity = Union[DeclarativeMeta, EntityBaseAddon]


class OrmDBEntityAccessor():
    """this class defines how to access the db entities, so session instance is required
        as the first argument when defining or overriding functions

            - select(): select database with or without keys and return a list of entities
            - load(): like select but just retunr first matched entity 
            - delete(): delete a list of entities
            - add(): insert one entity but not replace if it exists
            - merge(): insert or replace one entity
            - set_attribute(): update entity columns
            - refresh(): refresh entity from database
            - flush(): session flushing
            - rollback(): session rollback
            - save(): session commit
    """

    def __init__(self, entity_cls: Entity = None):
        super().__init__()
        if entity_cls is not None:
            self.set_entity_cls(entity_cls)

    def set_entity_cls(self, entity_cls: EntityBaseAddon) -> None:
        self.entity_cls = entity_cls

    def select(self, sess: Session, **kwargs) -> List[Entity]:
        if len(kwargs) > 0:
            qobj = sess.query(self.entity_cls).filter_by(**kwargs)
        else:
            qobj = sess.query(self.entity_cls)

        return [o for o in qobj]

    def load(self, sess: Session, **kwargs) -> Entity:
        if len(kwargs) > 0:
            return sess.query(self.entity_cls).filter_by(**kwargs).first()

    def delete(self, sess: Session, entities, **kwargs) -> None:
        if not isinstance(entities, list):
            entities = [entities]

        for entity in entities:
            sess.delete(entity)

    def add(self, sess: Session, **kwargs) -> Entity:
        entity = self.entity_cls()
        sess.add(entity)
        self.set_attribute(sess, entity, False, **kwargs)
        return entity

    def merge(self, sess: Session, **kwargs) -> Entity:
        pkeys = self.entity_cls.get_primary_key_args(**kwargs)
        entity = self.load(sess, **pkeys)
        if entity is None:
            entity = self.add(sess, **kwargs)
        else:
            self.set_attribute(
                sess, entity, **self.entity_cls.get_non_primary_key_args(**kwargs))
        return entity

    def set_attribute(self, sess: Session, entity: Entity, check_fix: bool = True, **kwargs) -> None:
        if isinstance(entity, EntityBaseAddon):
            entity.parameter_validation(check_fix, **kwargs)

        for k, v in kwargs.items():
            if hasattr(entity, k):
                if isinstance(getattr(entity, k), datetime):
                    if isinstance(v, str):
                        setattr(entity, k, str_to_datetime(v))
                    else:
                        setattr(entity, k, v)
                else:
                    setattr(entity, k, v)
            else:
                raise LocalizedMessageWarning(LocalCode_Invalid_Column, k)

    def refresh(self, sess: Session, entity: Entity) -> Entity:
        sess.refresh(entity)
        return entity

    def flush(self, sess: Session) -> None:
        try:
            changed = (len(sess.new), len(sess.dirty), len(sess.deleted))
            sess.flush()
            return changed
        except:
            self.rollback(sess)
            raise

    def rollback(self, sess: Session) -> None:
        sess.rollback()

    def save(self, sess: Session) -> None:
        try:
            changed = (len(sess.new), len(sess.dirty), len(sess.deleted))
            sess.commit()
            return changed
        except:
            self.rollback(sess)
            raise
