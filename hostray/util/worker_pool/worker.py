# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Monday, 4th November 2019 by hsky77 (howardlkung@gmail.com)
'''

import time
from typing import Callable, Any
from threading import Thread, Condition, Lock


class _BaseWorker(Thread):
    """hostray-customized python threading.Thread class"""

    def __init__(self, name: str = None):
        super().__init__(name=name)
        self._running = False

        self._run_method_lock = Lock()
        self.__resource_lock = None

        self._paused = False
        self._pause_lock = Lock()
        self._pause_cond = Condition(Lock())
        self.pause()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dispose()

    @property
    def is_started(self):
        return self._started.is_set()

    @property
    def resource_lock(self) -> Lock:
        """use this lock access resource synchronously"""
        self.__resource_lock = self.__resource_lock if self.__resource_lock else Lock()
        return self.__resource_lock

    def dispose(self) -> None:
        self._running = False
        self.resume()

    def start(self) -> None:
        self._running = True
        super().start()

    def pause(self) -> None:
        if not self._paused:
            self._paused = True
            with self._pause_lock:
                self._pause_cond.acquire()

    def resume(self) -> None:
        if self._paused:
            self._paused = False
            with self._pause_lock:
                self._pause_cond.notify()
                self._pause_cond.release()

    def run(self) -> None:
        """do not directly call this function, it will be called by thread automatically"""
        while self._running:
            with self._pause_cond:
                while self._paused:
                    self._pause_cond.wait()
            try:
                self._run()
            finally:
                self.pause()

    def _run(self) -> Any:
        """
        override this function to run something in thread, handle exception here to keep the thread alive
        """
        NotImplementedError()

    def _execute_function(self, func, *args, **kwargs) -> Any:
        """define how to execute the function"""
        return func(*args, **kwargs)


class Worker(_BaseWorker):
    """hostray-customized python threading.Thread class to execute functions"""

    def __init__(self, name: str = None):
        super().__init__(name=name)
        self._func = None
        self._args = None
        self._kwargs = None
        self._on_finish = None
        self._on_exception = None

    @property
    def is_func_running(self) -> bool:
        return self._func is not None

    def run_method(self,
                   func: Callable,
                   *args,
                   on_finish: Callable[[Any], None] = None,
                   on_exception: Callable[[Exception], None] = None,
                   **kwargs) -> bool:
        """return True if function will be executed, False if there is a function is running"""
        result = False
        with self._run_method_lock:
            if callable(func) and not self.is_func_running:
                self._func = func
                self._args = args
                self._kwargs = kwargs
                self._on_finish = on_finish
                self._on_exception = on_exception

                if not self.is_started:
                    self.start()

                self.resume()
                result = True
        return result

    def run_method_and_wait(self,
                            func: Callable,
                            *args,
                            **kwargs) -> Any:
        self._temp_result = None
        self._temp_exception = None

        def on_finish(result):
            self._temp_result = result

        def on_exception(e):
            self._temp_exception = e

        while not self.run_method(func, *args, on_finish=on_finish, on_exception=on_exception, **kwargs):
            time.sleep(0)

        while self.is_func_running:
            time.sleep(0)

        if self._temp_exception is not None:
            raise type(self._temp_exception)(str(self._temp_exception)
                                             ) from self._temp_exception

        return self._temp_result

    async def run_method_and_wait_async(self,
                                        func: Callable,
                                        *args,
                                        **kwargs) -> Any:
        import asyncio
        self._temp_result = None
        self._temp_exception = None

        def on_finish(result):
            self._temp_result = result

        def on_exception(e):
            self._temp_exception = e

        while not self.run_method(func, *args, on_finish=on_finish, on_exception=on_exception, **kwargs):
            await asyncio.sleep(0)
        while self.is_func_running:
            await asyncio.sleep(0)

        if self._temp_exception is not None:
            raise type(self._temp_exception)(str(self._temp_exception)
                                             ) from self._temp_exception

        return self._temp_result

    def _run(self) -> Any:
        if callable(self._func):
            try:
                self._result = self._execute_function(
                    self._func, *self._args, **self._kwargs)
                if callable(self._on_finish):
                    self._on_finish(self._result)
            except Exception as e:  # handle exception here to keep the thread alive
                if callable(self._on_exception):
                    self._on_exception(e)
            finally:
                self._func = None
                self._args = None
                self._kwargs = None
                self._on_finish = None
                self._on_exception = None


class FunctionQueueWorker(_BaseWorker):
    """worker that queues functions to execute"""

    def __init__(self, name: str = None):
        super().__init__(name)
        self.__tasks = []

    @property
    def pending_count(self) -> int:
        return len(self.__tasks)

    def run_method(self,
                   func: Callable,
                   *args,
                   on_finish: Callable[[Any], None] = None,
                   on_exception: Callable[[Exception], None] = None,
                   **kwargs) -> None:
        """func will be queued and run when the worker thread is free"""
        with self._run_method_lock:
            if callable(func):
                self.__tasks.append({
                    'func': func,
                    'on_finish': on_finish,
                    'on_exception': on_exception,
                    'args': args,
                    'kwargs': kwargs
                })

                if not self.is_started:
                    self.start()

                self.resume()

    def _run(self) -> Any:
        while len(self.__tasks) > 0:
            task = self.__tasks[0]

            try:
                result = self._execute_function(
                    task['func'], *task['args'], **task['kwargs'])
                if callable(task['on_finish']):
                    task['on_finish'](result)
            except Exception as e:
                if callable(task['on_exception']):
                    task['on_exception'](e)

            with self._run_method_lock:
                self.__tasks.pop(0)


class FunctionLoopWorker(_BaseWorker):
    """worker class loops a single function in one period before calling stop()"""

    def __init__(self, name: str = None, loop_interval_seconds: float = 1.0):
        super().__init__(name=name)
        self.__loop_interval_seconds = loop_interval_seconds
        self.__on_finish = None
        self.__on_exception = None
        self.stop()

    def dispose(self):
        super().dispose()
        self.stop()
        self.join()

    def stop(self):
        """stop looping"""
        self._func = None
        self._args = None
        self._kwargs = None
        self.__on_finish = None
        self.__on_exception = None

    def run_method(self,
                   func: Callable,
                   *args,
                   on_finish: Callable[[Any], None] = None,
                   on_exception: Callable[[Exception], None] = None,
                   **kwargs) -> None:
        """start looping function"""
        with self._run_method_lock:
            if self._func is None:
                self._func = func
                self._args = args
                self._kwargs = kwargs
                self.__on_finish = on_finish
                self.__on_exception = on_exception

                if not self.is_started:
                    self._running = True
                    self.start()

                self.resume()

    def _run(self):
        while callable(self._func):
            try:
                result = self._execute_function(
                    self._func, *self._args, **self._kwargs)
                if callable(self.__on_finish):
                    self.__on_finish(result)
            except Exception as e:
                if callable(self.__on_exception):
                    self.__on_exception(e)
            finally:
                time.sleep(self.__loop_interval_seconds)
