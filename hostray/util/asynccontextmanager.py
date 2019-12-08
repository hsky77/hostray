# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
this code was modified from the source package "async_generator(https://pypi.org/project/async_generator/)",
to make _AsyncGeneratorContextManager inherits from typing.AsyncContextManager and contextlib.ContextDecorator

Last Updated:  Monday, 4th November 2019 by hsky77 (howardlkung@gmail.com)
'''

import sys
from typing import AsyncContextManager, AsyncGenerator, Callable
from contextlib import ContextDecorator
from inspect import isasyncgenfunction
from functools import wraps

from .localization import BaseLocal
from .constants import (LocalCode_Not_Async_Gen, LocalCode_Not_Yield,
                        LocalCode_Not_Stop, LocalCode_Not_Stop_After_Throw)


class _AsyncGeneratorContextManager(ContextDecorator, AsyncContextManager):
    """Helper for @asynccontextmanager decorator."""

    def __init__(self, func, args, kwds):
        if not isasyncgenfunction(func):
            raise TypeError(BaseLocal.get_message(LocalCode_Not_Async_Gen))

        self.func, self.args, self.kwds = func, args, kwds
        self.gen = func(*args, **kwds).__aiter__()

    def _recreate_cm(self):
        # _GCM instances are one-shot context managers, so the
        # CM must be recreated each time a decorated function is
        # called
        return self.__class__(self.func, self.args, self.kwds)

    async def __aenter__(self):
        try:
            return await self.gen.asend(None)
        except StopAsyncIteration:
            raise RuntimeError(BaseLocal.get_message(
                LocalCode_Not_Yield)) from None

    async def __aexit__(self, type, value, traceback):
        if type is None:
            try:
                await self.gen.asend(None)
            except StopAsyncIteration:
                return False
            else:
                raise RuntimeError(BaseLocal.get_message(LocalCode_Not_Stop))
        else:
            if value is None:
                # Need to force instantiation so we can reliably
                # tell if we get the same exception back
                value = type()
            try:
                await self.gen.athrow(type, value, traceback)
                raise RuntimeError(
                    BaseLocal.get_message(LocalCode_Not_Stop_After_Throw)
                )
            except StopAsyncIteration as exc:
                # Suppress StopIteration *unless* it's the same exception that
                # was passed to throw().  This prevents a StopIteration
                # raised inside the "with" statement from being suppressed.
                return exc is not value
            except RuntimeError as exc:
                # Don't re-raise the passed in exception. (issue27122)
                if exc is value:
                    return False
                # Likewise, avoid suppressing if a StopIteration exception
                # was passed to throw() and later wrapped into a RuntimeError
                # (see PEP 479).
                if (type is StopIteration or type is StopAsyncIteration) and exc.__cause__ is value:
                    return False
                raise
            except:
                # only re-raise if it's *not* the exception that was
                # passed to throw(), because __exit__() must not raise
                # an exception unless __exit__() itself failed.  But throw()
                # has to raise the exception to signal propagation, so this
                # fixes the impedance mismatch between the throw() protocol
                # and the __exit__() protocol.
                #
                if sys.exc_info()[1] is value:
                    return False
                raise
            raise RuntimeError(BaseLocal.get_message(
                LocalCode_Not_Stop_After_Throw))


def asynccontextmanager(func: AsyncGenerator):
    """@asynccontextmanager decorator

    Typical usage:

        @asynccontextmanager
        def some_generator(<arguments>):
            <setup>
            try:
                yield <value>
            finally:
                <cleanup>

    This makes this:

        async with some_generator(<arguments>) as <variable>:
            <body>

    equivalent to this:

        <setup>
        try:
            <variable> = <value>
            <body>
        finally:
            <cleanup>
    """

    @wraps(func)
    def helper(*args, **kwds):
        return _AsyncGeneratorContextManager(func, args, kwds)
    return helper
