# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Tuesday, 12th November 2019 by hsky77 (howardlkung@gmail.com)
'''

import asyncio
from enum import Enum
from datetime import datetime

from ..util import Callbacks, PY_DT_Converter, DOT_NET_DT_Converter, str_to_datetime
from .base import UnitTestCase


class TestCallbackType(Enum):
    Event_A = 'a'
    Event_A_Async = 'a_async'


class UtilTestCase(UnitTestCase):
    def test(self):
        self.test_dt()
        self.test_callback()

    def test_dt(self):
        now = datetime.now().replace(microsecond=0)
        self.assertEqual(now, PY_DT_Converter.str_to_dt(
            PY_DT_Converter.dt_to_str(now)))

        self.assertEqual(now, DOT_NET_DT_Converter.str_to_dt(
            DOT_NET_DT_Converter.dt_to_str(now)))

        py_time = '2019-07-07 16:34:22'
        dnet_time = '2019-07-07T16:34:22'
        self.assertEqual(str_to_datetime(py_time),
                         datetime(2019, 7, 7, 16, 34, 22))
        self.assertEqual(str_to_datetime(dnet_time),
                         datetime(2019, 7, 7, 16, 34, 22))

    def test_callback(self, callbacks: Callbacks = None):
        cb = callbacks or Callbacks(TestCallbackType)
        cb.add_callback(TestCallbackType.Event_A, UtilTestCase.test_func)
        cb.add_callback(TestCallbackType.Event_A_Async,
                        UtilTestCase.test_func_async)

        cb.execute_callback(TestCallbackType.Event_A, self, 1, kwindex=2)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(cb.execute_callback_async(
            TestCallbackType.Event_A_Async, self, 1, kwindex=2))

    def test_func(self, i, kwindex):
        self.assertEqual(i, 1)
        self.assertEqual(kwindex, 2)

    async def test_func_async(self, i, kwindex):
        self.assertEqual(i, 1)
        self.assertEqual(kwindex, 2)
