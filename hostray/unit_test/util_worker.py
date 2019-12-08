# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Sunday, 10th November 2019 by hsky77 (howardlkung@gmail.com)
'''

import time
import random
import asyncio

from ..util import Worker, FunctionLoopWorker, FunctionQueueWorker
from .base import UnitTestCase


class WorkerTestCase(UnitTestCase):
    def test(self):
        self.test_pools()
        self.test_workers()

    def test_pools(self):
        """test worker pool both sync and async function"""
        from ..util import AsyncWorkerPool
        loop = asyncio.get_event_loop()
        worker_count = 4
        ap = AsyncWorkerPool(worker_limit=worker_count)

        def foo(index, count):
            self.assertIsNotNone(index)
            return index

        def foo_raise_exception(index, kwindex):
            self.assertIsNotNone(index)
            raise Exception('This is from foo_raise_exception()')

        with ap.reserve_worker() as identity:
            result = []
            result.append(ap.run_method(foo, 1, 1, identity=identity))
            result.append(ap.run_method(foo, 1, 2, identity=identity))
            try:
                result.append(ap.run_method(
                    foo_raise_exception, 1, 3, identity=identity))
            except Exception as e:
                self.assertEqual(str(e), 'This is from foo_raise_exception()')

        async def async_foo_alone(index):
            result = []
            result.append(foo(index, 1))
            result.append(foo(index, 2))
            try:
                result.append(foo_raise_exception(1, 3))
            except Exception as e:
                self.assertEqual(
                    str(e), 'This is from foo_raise_exception()')
            return result

        async def async_foo(index):
            result = []
            result.append(await ap.run_method_async(foo, index, 1))
            result.append(await ap.run_method_async(foo, index, 2))
            try:
                result.append(await ap.run_method_async(foo_raise_exception, index, 3))
            except Exception as e:
                self.assertEqual(
                    str(e), 'This is from foo_raise_exception()')

            async with ap.reserve_worker_async() as identity:
                result.append(await ap.run_method_async(foo, index, 1, identity=identity))
                result.append(await ap.run_method_async(foo, index, 2, identity=identity))
                try:
                    result.append(await ap.run_method_async(foo_raise_exception, index, 3, identity=identity))
                except Exception as e:
                    self.assertEqual(
                        str(e), 'This is from foo_raise_exception()')

            return result

        futures = []
        count = 5000
        for i in range(count):
            futures.append(asyncio.ensure_future(async_foo(i)))

        loop.run_until_complete(asyncio.wait(futures))

        self.assertLessEqual(len(ap.workers), worker_count)
        ap.dispose()

        for i in range(count):
            results = futures[i].result()
            self.assertIsInstance(results, list)
            for result in results:
                self.assertEqual(result, i)

    def test_workers(self):
        """test function and callback have been executed properly, it should takes 2~3 secs"""

        self.check_exp = False
        self.loop_count = 0

        def foo(index, kwindex):
            self.assertIs(index, 1)
            self.assertIs(kwindex, 2)
            self.loop_count = self.loop_count + 1
            return index

        def foo_raise_exception(index, kwindex):
            self.assertIs(index, 1)
            self.assertIs(kwindex, 2)
            self.loop_count = self.loop_count + 1
            raise Exception('This is from foo_raise_exception()')

        def on_finish(result):
            self.assertIs(result, 1)

        def on_exception(e):
            self.assertEqual(str(e), 'This is from foo_raise_exception()')
            self.check_exp = True

        with Worker() as worker:
            worker.run_method(foo, 1, kwindex=2,
                              on_finish=on_finish, on_exception=on_exception)

            self.check_exp = True
            worker.run_method(foo_raise_exception, 1, kwindex=2,
                              on_finish=on_finish, on_exception=on_exception)

            self.assertTrue(self.check_exp)

        with FunctionQueueWorker() as worker:
            self.check_exp = False
            worker.run_method(foo, 1, kwindex=2, on_finish=on_finish,
                              on_exception=on_exception)

            worker.run_method(foo_raise_exception, 1, kwindex=2, on_finish=on_finish,
                              on_exception=on_exception)

            start_time = time.time()
            while worker.pending_count > 0:
                self.assertGreaterEqual(3, time.time() - start_time)

            self.assertTrue(self.check_exp)

        with FunctionLoopWorker(loop_interval_seconds=0.1) as worker:
            self.check_exp = False
            self.loop_count = 0
            wait_time = 0.5

            worker.run_method(foo, 1, kwindex=2, on_finish=on_finish,
                              on_exception=on_exception)

            start_time = time.time()
            while time.time() - start_time < wait_time:
                pass

            self.assertGreaterEqual(self.loop_count, 2)

            self.loop_count = 0
            worker.run_method(foo_raise_exception, 1, kwindex=2, on_finish=on_finish,
                              on_exception=on_exception)

            start_time = time.time()
            while time.time() - start_time < wait_time:
                pass

            self.assertGreaterEqual(self.loop_count, 2)
