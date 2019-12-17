# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Monday, 4th November 2019 by hsky77 (howardlkung@gmail.com)
'''


import time
import asyncio
from enum import Enum
from typing import Any, Callable

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import DeclarativeMeta

from .. import (FunctionQueueWorker, AsyncWorkerPool, LocalizedMessageException,
                LocalCode_Missing_File_Path, LocalCode_Missing_Host, LocalCode_Missing_User,
                LocalCode_Missing_Password, LocalCode_Missing_DB_Name)


class DB_MODULE_NAME(Enum):
    SQLITE_MEMORY = 'sqlite:///:memory:'
    SQLITE_FILE = 'sqlite:///{}'
    MYSQL = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'


def get_connection_string(db_module: DB_MODULE_NAME, **kwargs) -> str:
    connect_string = db_module.value

    if db_module == DB_MODULE_NAME.SQLITE_FILE:
        file_name = kwargs.get('file_name')
        if file_name is None:
            raise LocalizedMessageException(LocalCode_Missing_File_Path)
        connect_string = db_module.value.format(file_name)
    elif db_module == DB_MODULE_NAME.MYSQL:
        host = kwargs.get('host')
        if host is None:
            raise LocalizedMessageException(LocalCode_Missing_Host)

        user = kwargs.get('user')
        if user is None:
            raise LocalizedMessageException(LocalCode_Missing_User)

        password = kwargs.get('password')
        if password is None:
            raise LocalizedMessageException(LocalCode_Missing_Password)

        db_name = kwargs.get('db_name')
        if db_name is None:
            raise LocalizedMessageException(LocalCode_Missing_DB_Name)

        port = kwargs.get('port')
        if port is None:
            port = 3306

        connect_string = db_module.value.format(
            user, password, host, port, db_name)

    return connect_string


def get_session_maker(db_module: DB_MODULE_NAME, declared_entity_base: DeclarativeMeta, autoflush: bool = False, **kwargs) -> Session:
    connect_args = {}
    engine_args = {}
    engine = create_engine(get_connection_string(db_module, **kwargs),
                           connect_args=connect_args, **engine_args)
    declared_entity_base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=autoflush)


class _OrmAccessWorker(FunctionQueueWorker):
    """worker class keeps the session and connection to execute orm entity object or SQLs"""

    def __init__(self, name: str = None):
        super().__init__()
        super().__init__(name=name)
        self.__sess_maker = None
        self.__sess = None

    def set_orm_engine(self, db_module: DB_MODULE_NAME, declared_entity_base: DeclarativeMeta, autoflush: bool = False, **kwargs) -> None:
        with self.resource_lock:
            self.__sess_maker = None
            self.db_module = db_module
            self.declared_entity_base = declared_entity_base
            self.autoflush = autoflush
            self.db_kwargs = kwargs

    def close_session(self, *args, **kwargs) -> None:
        """this function should also be called by worker thread"""
        if self.__sess is not None:
            self.__sess.close()
        self.__sess = None

        if self.__sess_maker is not None:
            self.__sess_maker.close_all()

    def _execute_function(self, func: Callable, *args, **kwargs) -> Any:
        if self.__sess is None:
            with self.resource_lock:
                if self.__sess_maker is None:
                    self.__sess_maker = get_session_maker(
                        self.db_module, self.declared_entity_base, self.autoflush, **self.db_kwargs)

                self.__sess = self.__sess_maker()
        return func(self.__sess, *args, **kwargs)


class OrmAccessWorkerPool(AsyncWorkerPool):
    """orm db executor worker pool"""

    def __init__(self, pool_name: str = None, worker_limit: int = 1):
        super().__init__(pool_name, worker_limit)
        self.enable_orm_log(False)

    def enable_orm_log(self, echo: bool = False) -> None:
        import logging
        sqla_logger = logging.getLogger('sqlalchemy')
        sqla_logger.propagate = echo

    def set_session_maker(self, db_module: DB_MODULE_NAME, declared_entity_base: DeclarativeMeta, autoflush: bool = False, **kwargs) -> None:
        self.db_module = db_module
        self.declared_entity_base = declared_entity_base
        self.autoflush = autoflush
        self.db_kwargs = kwargs

        for w in self.workers:
            w.set_orm_engine(db_module, declared_entity_base,
                             autoflush, **kwargs)

    def dispose(self) -> None:
        self.reset_connection()
        super().dispose()

    def reset_connection(self) -> None:
        """
        reset db worker sessions and connection

        attention: do not call this function in the clauses of 'with reserve_worker()' and 'with reserve_worker_async()'
        """
        self.broadcast_method('close_session')

    async def reset_connection_async(self) -> None:
        """
        reset db worker sessions and connection

        attention: do not call this function in the clauses of 'with reserve_worker()' and 'with reserve_worker_async()'
        """
        await self.broadcast_method_async('close_session')

    def _create_worker(self, name: str) -> _OrmAccessWorker:
        worker = _OrmAccessWorker(name=name)
        worker.set_orm_engine(self.db_module, self.declared_entity_base,
                              self.autoflush, **self.db_kwargs)
        return worker
