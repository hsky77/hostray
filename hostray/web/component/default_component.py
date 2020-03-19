# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
server loads all default components in hostray.web.component.DefaultComponentTypes when starting

    LocalizationComponent:

        - managing localized message via config setting such as:

        component:                                      # component block of server_config.yaml
            localization:                               # indicate DefaultComponentTypes.Localization
                dir: <dir path of language files>

    LoggerComponent:

        - managing logger via config setting such as:

        component:                                      # component block of server_config.yaml
            logger:                                     # indicate DefaultComponentTypes.Logger
                dir: <dir path store log files>

    TaskQueue:

        - queue func (task) to execute and balances tasks with worker_count

        component:                                      # component block of server_config.yaml
            task_queue:                                 # indicate DefaultComponentTypes.TaskQueue
                worker_count: <number of workers>

    WorkerPoolComponent:

        - managing worker pool by server config

        component:                                      # component block of server_config.yaml
            worker_pool:                                # indicate DefaultComponentTypes.WorkerPool
                <pool_id>: <number limit of workers>

    CallbackComponent:

        - managing callback function by enum types, no configuration settings needed

Last Updated:  Tuesday, 5th November 2019 by hsky77 (howardlkung@gmail.com)
'''


from typing import Callable, Any, List, Dict
from enum import Enum

from hostray.util import (get_Hostray_logger,
                          setting_loggers,
                          join_path,
                          configure_colored_logging,
                          HostrayLogger,
                          Callbacks,
                          AsyncWorkerPool,
                          FunctionQueueWorker)

from .. import HostrayWebException, LocalCode_Comp_Missing_Parameter

from . import Component, DefaultComponentTypes, ComponentManager, ComponentTypes


class LocalizationComponent(Component):
    """default component for managing localized message by config setting"""

    def init(self, component_manager: ComponentManager, lang: str = 'en', **kwargs) -> None:
        import os
        from hostray.util import BaseLocal
        self.local = BaseLocal

        self.dir = kwargs.get('dir', None)
        if self.dir is not None:
            self.dir = join_path(kwargs.get('root_dir', ''), self.dir)
            self.local.import_csvs_from_directory(self.dir)

        # update tornado http messages: not all of the status has localized message
        from tornado.web import httputil
        from .. import HttpLocal

        if lang is not None:
            self.local.set_language(lang)
            HttpLocal.set_language(lang)

        for code in [x.value for x in httputil.responses.keys()]:
            if HttpLocal.has_message(code):
                httputil.responses[code] = HttpLocal.get_message(code)

    def info(self) -> str:
        return {**super().info(), **{'info': self.local.get_info()}}

    @property
    def current_language(self) -> str:
        return self.local.current_language

    def set_language(self, lang: str) -> None:
        self.local.set_language(lang)

    def get_message(self, code: str, *args) -> str:
        """convert to localized message with code and following parameters"""
        return self.local.get_message(code, *args)


class LoggerComponent(Component):
    """default component for managing logger by server config"""

    default_loggers = ['tornado.access',
                       'tornado.application',
                       'tornado.general',
                       'sqlalchemy',
                       'sqlalchemy.orm.mapper.Mapper']

    def __init__(self, component_type: ComponentTypes):
        super().__init__(component_type)
        configure_colored_logging()

    def init(self, component_manager: ComponentManager, **kwargs) -> None:
        self.dir = kwargs.get('dir')
        self.log_to_resource = kwargs.get('log_to_resource', False)
        if self.dir:
            self.dir = join_path(kwargs.get('root_dir', ''), self.dir)

        setting_loggers(self.default_loggers, self.dir,
                        log_to_resource=self.log_to_resource)

        self.set_default_logger_echo(False)

    def set_default_logger_echo(self, echo: bool) -> None:
        from logging import getLogger, ERROR, DEBUG
        for name in self.default_loggers:
            logger = getLogger(name)
            logger.setLevel(ERROR if not echo else DEBUG)

    def get_logger(self, name: str, sub_dir: str = '', mode: str = 'a', encoding: str = 'utf-8',
                   echo: bool = False) -> HostrayLogger:
        """create and return logger object, sub_dir appends the path to configured log path"""
        from logging import getLogger, ERROR, DEBUG
        if self.dir:
            sub_dir = join_path(self.dir, sub_dir)
        else:
            sub_dir = None
        logger = get_Hostray_logger(name, sub_dir, mode,
                                    encoding, self.log_to_resource)
        logger.setLevel(ERROR if not echo else DEBUG)
        return logger


class CallbackComponent(Component):
    """default component for managing callback function by enum types"""

    def init(self, component_manager: ComponentManager, *arugs, **kwargs) -> None:
        self._callback_manager = {}

    def get_callback_obj(self, enum_cls: Enum) -> Callbacks:
        if not enum_cls in self._callback_manager:
            self._callback_manager[enum_cls] = Callbacks(enum_cls)
        return self._callback_manager[enum_cls]

    def add_callback(self, callback_enum_type: Enum, callback: Callable) -> None:
        if isinstance(callback_enum_type, Enum):
            enum_cls = type(callback_enum_type)
            if not enum_cls in self._callback_manager:
                self._callback_manager[enum_cls] = Callbacks(enum_cls)

            self._callback_manager[enum_cls].add_callback(
                callback_enum_type, callback)

    def remove_callback(self, callback_enum_type: Enum, callback: Callable) -> None:
        if isinstance(callback_enum_type, Enum):
            enum_cls = type(callback_enum_type)
            if enum_cls in self._callback_manager:
                self._callback_manager[enum_cls].remove_callback(
                    callback_enum_type, callback)

    def execute_callback(self, callback_enum_type: Enum, *args, **kwargs) -> None:
        from tornado.ioloop import IOLoop
        if isinstance(callback_enum_type, Enum):
            enum_cls = type(callback_enum_type)
            if enum_cls in self._callback_manager:
                self._callback_manager[enum_cls].execute_callback(
                    callback_enum_type, *args, **kwargs)

    async def execute_callback_async(self, callback_enum_type: Enum, *args, **kwargs) -> None:
        if isinstance(callback_enum_type, Enum):
            enum_cls = type(callback_enum_type)
            if enum_cls in self._callback_manager:
                await self._callback_manager[enum_cls].execute_callback_async(
                    callback_enum_type, *args, **kwargs)


class TaskQueueComponent(Component):
    """default component to queue func to execute"""

    def init(self, component_manager: ComponentManager, worker_count: int = 1, **kwargs) -> None:
        self.worker_count = worker_count
        self._queue_workers: List[FunctionQueueWorker] = []
        self.disposing = False

    def run_method_in_queue(self, func: Callable, *args,
                            on_finish: Callable[[Any], None] = None,
                            on_exception: Callable[[Exception], None] = None,
                            **kwargs) -> None:
        if not self.disposing:
            worker: FunctionQueueWorker = None

            if len(self._queue_workers) < self.worker_count:
                worker = FunctionQueueWorker(
                    'TaskQueue_{}'.format(len(self._queue_workers)))
                self._queue_workers.append(worker)
            else:
                for w in self._queue_workers:
                    worker = worker if worker is not None and worker.pending_count < w.pending_count else w

            worker.run_method(func, *args, on_finish=on_finish,
                              on_exception=on_exception, **kwargs)

    def info(self) -> Dict:
        return {**super().info(), **{
            'info': {
                'maximum_of_workers': self.worker_count,
                'pendings': {w.name: w.pending_count for w in self._queue_workers}
            }
        }}

    def dispose(self, component_manager: ComponentManager) -> None:
        self.disposing = True
        for w in self._queue_workers:
            while w.pending_count > 0:
                pass
            w.dispose()


class WorkerPoolComponent(Component):
    """default component for managing worker pool by server config"""

    def init(self, component_manager: ComponentManager, **kwargs) -> None:
        self.pools = {}

        for pool_id, limit in {k: v for k, v in kwargs.items() if not 'root_dir' in k}.items():
            self.set_pool(pool_id, limit)

        if len(self.pools) == 0:  # add defualt pull
            self.set_pool()

    def set_pool(self, pool_id: str = 'default', worker_limit: int = 3) -> None:
        """add or replace a pool object of pool id"""
        if pool_id in self.pools:
            self.pools[pool_id].dispose()
            self.pools.pop(pool_id)

        if not pool_id in self.pools:
            self.pools[pool_id] = AsyncWorkerPool(
                pool_id, worker_limit=worker_limit)

    def info(self) -> Dict:
        return {**super().info(), **{
            'info': {
                k: v.info() for k, v in self.pools.items()
            }
        }}

    def run_method(self, func: Callable, *args, pool_id: str = 'default', **kwargs) -> Any:
        return self.pools[pool_id].run_method(func, *args, **kwargs)

    async def run_method_async(self, func: Callable, *args, pool_id: str = 'default', **kwargs) -> Any:
        return await self.pools[pool_id].run_method_async(func, *args, **kwargs)

    def dispose(self, component_manager: ComponentManager) -> None:
        for _, v in self.pools.items():
            v.dispose()
