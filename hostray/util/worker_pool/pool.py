# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Monday, 4th November 2019 by hsky77 (howardlkung@gmail.com)
'''


import time
import asyncio
from typing import Any, Callable, List, Dict
from contextlib import contextmanager

from .worker import FunctionQueueWorker
from ..asynccontextmanager import asynccontextmanager


class PoolWorkerExecutor():
    def __init__(self, worker: FunctionQueueWorker):
        self._worker = worker
        self._done = False
        self._exception = None
        self._result = None

    def run_method(self, func: Callable, *args, **kwargs) -> Any:
        self._done = False
        self._worker.run_method(func, *args, on_finish=self._on_finish,
                                on_exception=self._on_exception, **kwargs)
        while not self._done:
            time.sleep(0)
        return self.get_result()

    async def run_method_async(self, func: Callable, *args, **kwargs) -> Any:
        self._done = False
        self._worker.run_method(func, *args, on_finish=self._on_finish,
                                on_exception=self._on_exception, **kwargs)
        while not self._done:
            await asyncio.sleep(0)
        return self.get_result()

    def get_result(self) -> Any:
        if self._done:
            if self._exception is not None:
                raise self._exception
            else:
                return self._result
        return

    def _on_finish(self, result: Any) -> None:
        self._result = result
        self._done = True

    def _on_exception(self, e: Exception) -> None:
        self._exception = e
        self._done = True


class WorkerPool():
    KEY_IDENTITY = 'identity'
    KEY_WORKER = 'worker'

    def __init__(self, pool_name: str = None, worker_limit: int = 4):
        self._pool_name = pool_name or type(self).__name__
        self._q = []
        self.__worker_limit = worker_limit
        self.__disposing = False

    @property
    def workers(self) -> List[FunctionQueueWorker]:
        return [w[self.KEY_WORKER] for w in self._q]

    def dispose(self) -> None:
        self.__disposing = True

        for w in self._q:
            w[self.KEY_WORKER].dispose()

    def info(self) -> Dict:
        """return the dict show the current condition of this pool"""
        return [{
            'name': w[self.KEY_WORKER].name,
            'identity': w[self.KEY_IDENTITY],
            'pending_task': w[self.KEY_WORKER].pending_count
        } for w in self._q]

    def run_method(self, func: Callable, *args, identity: str = None, **kwargs) -> Any:
        """execute function, note this causes current thread blocking"""
        executor = self._get_free_executor(identity=identity)
        return executor.run_method(func, *args, **kwargs)

    def broadcast_method(self, func_name: str, *args, **kwargs) -> List[Any]:
        """use this function to force each worker execute some function if it has such as release or refresh resources"""
        results = []
        identity = self._get_identity()
        for iw in self._q:
            while iw[self.KEY_WORKER].pending_count > 0:
                time.sleep(0)
            iw[self.KEY_IDENTITY] = identity
            if hasattr(iw[self.KEY_WORKER], func_name):
                pool_worker = PoolWorkerExecutor(iw[self.KEY_WORKER])
                results.append(pool_worker.run_method(
                    getattr(iw[self.KEY_WORKER], func_name), *args, **kwargs))

        for iw in self._q:
            iw[self.KEY_IDENTITY] = None
        return results

    @contextmanager
    def reserve_worker(self):
        """use with clause to reserve the same worker for execute multiple functions"""
        try:
            identity = self._get_identity()
            while not self._reserve_worker(identity):
                time.sleep(0)
            yield identity
        finally:
            self._cancel_reservation(identity)

    def _get_free_executor(self, identity: str = None) -> PoolWorkerExecutor:
        """getting a worker is free to execute function, also reserve worker if identity is specified"""
        if self.__disposing:
            return None

        worker = None
        for exe in self._q:
            if identity is not None and identity is exe[self.KEY_IDENTITY]:
                worker = exe[self.KEY_WORKER]
                break

        if worker is None:
            if len(self._q) < self.__worker_limit:
                worker = self._create_worker(
                    '{}_{}'.format(self._pool_name, len(self._q)))
                self._q.append({self.KEY_IDENTITY: identity,
                                self.KEY_WORKER: worker})
            else:
                m = None
                index = -1
                for i in range(len(self._q)):
                    if self._q[i][self.KEY_IDENTITY] is None:
                        if m is None:
                            m = self._q[i][self.KEY_WORKER].pending_count
                            index = i
                        else:
                            if m > self._q[i][self.KEY_WORKER].pending_count:
                                m = self._q[i][self.KEY_WORKER].pending_count
                                index = i
                if index > -1:
                    worker = self._q[index][self.KEY_WORKER]

        return PoolWorkerExecutor(worker) if worker else None

    def _get_identity(self) -> str:
        from ..utils import generate_base64_uid
        return generate_base64_uid()

    def _reserve_worker(self, identity: str) -> bool:
        return self._get_free_executor(identity=identity) is not None

    def _cancel_reservation(self, identity: str) -> None:
        if identity is not None:
            for i in range(0, len(self._q)):
                if identity is self._q[i][self.KEY_IDENTITY]:
                    self._q[i][self.KEY_IDENTITY] = None

    def _create_worker(self, name: str) -> FunctionQueueWorker:
        return FunctionQueueWorker(name=name)


class AsyncWorkerPool(WorkerPool):
    """add async function to WorkerPool"""
    @asynccontextmanager
    async def reserve_worker_async(self) -> str:
        """use with clause to reserve the same worker for execute multiple functions"""
        try:
            identity = self._get_identity()
            while not self._reserve_worker(identity):
                await asyncio.sleep(0)

            yield identity
        finally:
            self._cancel_reservation(identity)

    async def run_method_async(self, func: Callable, *args, identity: str = None, **kwargs) -> Any:
        executor = self._get_free_executor(identity=identity)
        return await executor.run_method_async(func, *args, **kwargs)

    async def broadcast_method_async(self, func_name: str, *args, **kwargs) -> List[Any]:
        """use this function to force each worker execute some function if it has such as release or refresh resources"""
        results = []
        identity = self._get_identity()
        for iw in self._q:
            while iw[self.KEY_WORKER].pending_count > 0:
                asyncio.sleep(0)
            iw[self.KEY_IDENTITY] = identity
            if hasattr(iw[self.KEY_WORKER], func_name):
                pool_worker = PoolWorkerExecutor(iw[self.KEY_WORKER])
                results.append(await pool_worker.run_method_async(
                    getattr(iw[self.KEY_WORKER], func_name), *args, **kwargs))

        for iw in self._q:
            iw[self.KEY_IDENTITY] = None
        return results
