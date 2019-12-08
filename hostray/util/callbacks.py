# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Monday, 4th November 2019 by hsky77 (howardlkung@gmail.com)
'''


from enum import Enum
from typing import Callable, Any, Union

from . import LocalizedMessageException
from .constants import LocalCode_Not_Valid_Enum, LocalCode_Not_ASYNC_FUNC


class Callbacks():
    """
    Class uses enum to group and manage the callbacks (events). 
    Basically, this is useful to send events between class and controller instances.
    Note: there is not arguments check, so be careful when executing the callbacks
    """

    def __init__(self, callback_enum_cls: Enum):
        self.callbacks = {}
        self.callback_type_cls = callback_enum_cls

    def add_callback(self, callback_enum: Union[Enum, str], callback: Callable) -> None:
        callback_type = self.callback_type_cls(callback_enum)
        if callable(callback):
            if callback_type in self.callbacks:
                self.callbacks[callback_type].add(callback)
            else:
                self.callbacks[callback_type] = set()
                self.callbacks[callback_type].add(callback)

    def remove_callback(self, callback_enum: Union[Enum, str], callback: Callable) -> None:
        callback_type = self.callback_type_cls(callback_enum)
        if callable(callback):
            if callback_type in self.callbacks:
                self.callbacks[callback_type].remove(callback)

    def execute_callback(self, callback_enum: Union[Enum, str], *arugs, **kwargs) -> Any:
        if isinstance(callback_enum, self.callback_type_cls):
            if callback_enum in self.callbacks:
                for cb in self.callbacks[callback_enum]:
                    cb(*arugs, **kwargs)
        else:
            raise LocalizedMessageException(
                LocalCode_Not_Valid_Enum, callback_enum, self.callback_type_cls)

    async def execute_callback_async(self, callback_enum: Union[Enum, str], *arugs, **kwargs):
        from inspect import iscoroutinefunction
        if isinstance(callback_enum, self.callback_type_cls):
            if callback_enum in self.callbacks:
                for cb in self.callbacks[callback_enum]:
                    if iscoroutinefunction(cb):
                        await cb(*arugs, **kwargs)
                    else:
                        raise LocalizedMessageException(
                            LocalCode_Not_ASYNC_FUNC, cb)
        else:
            raise LocalizedMessageException(
                LocalCode_Not_Valid_Enum, callback_enum, self.callback_type_cls)
