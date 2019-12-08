# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Tuesday, 5th November 2019 by hsky77 (howardlkung@gmail.com)
'''

import sys
import traceback
from enum import Enum
from datetime import datetime
from typing import Any, Dict

from tornado.web import RequestHandler, HTTPError

from .base import ControllerAddon, HostrayWebFinish

from .. import (LocalCode_Missing_Required_Parameter, LocalCode_Incorrect_Type, LocalizedMessageWarning,
                LocalCode_Not_Valid_Column)


class RESTfulMethodType(Enum):
    GET = 'GET'
    POST = 'POST'
    PATCH = 'PATCH'
    PUT = 'PUT'
    DELETE = 'DELETE'
    OPTION = 'OPTION'


class RequestController(ControllerAddon, RequestHandler):
    """base http request hanlder class of hostray"""

    def __init__(self, application, request, **kwds):
        self.allowed_arugments: dict = {k.value: {}
                                        for k in RESTfulMethodType}  # allow any arguments
        self.required_arugments: dict = {
            k.value: [] for k in RESTfulMethodType}  # not require any arguments

        ControllerAddon.__init__(self, application, request, **kwds)
        RequestHandler.__init__(self, application, request, **kwds)
        self.__cache: dict = None

    @property
    def cache(self) -> Dict:
        if self.__cache is None:
            from hostray.web.component import OptionalComponentTypes
            from hostray.web.component.optional_component import MemoryCacheComponent
            cache_comp: MemoryCacheComponent = self.application.component_manager.get_component(
                OptionalComponentTypes.MemoryCache)

            if cache_comp is not None:
                cache_id = self.get_secure_cookie('cache_id')
                if cache_id is None:
                    self.__cache, cache_id = cache_comp.get()
                else:
                    cache_id = cache_id.decode('utf-8')
                    self.__cache, cache_id = cache_comp.get(cache_id)
                self.set_secure_cookie('cache_id', cache_id)
        return self.__cache

    def get_allowed_arguments(self) -> Dict[str, Any]:
        keys = {}
        for k in self.request.arguments:
            if len(self.allowed_arugments[self.request.method]) > 0:
                if not k in self.allowed_arugments[self.request.method]:
                    raise HostrayWebFinish(
                        LocalCode_Not_Valid_Column, k)
                else:
                    try:
                        value = self.get_argument(k)
                        if self.allowed_arugments[self.request.method][k] is datetime:
                            # datetime type
                            from hostray.util import str_to_datetime
                            keys[k] = str_to_datetime(value)
                        else:
                            keys[k] = self.allowed_arugments[self.request.method][k](
                                value)
                    except:
                        raise HostrayWebFinish(
                            LocalCode_Incorrect_Type, value, self.allowed_arugments[self.request.method][k])
            else:
                keys[k] = self.get_argument(k)
        return keys

    def get_required_valid_arguments(self) -> Dict[str, Any]:
        keys: dict = self.get_allowed_arguments()
        for k in self.required_arugments[self.request.method]:
            if not k in keys:
                raise HostrayWebFinish(
                    LocalCode_Missing_Required_Parameter, k)
        return {k: v for k, v in self.get_allowed_arguments().items() if k in self.required_arugments[self.request.method]}

    def get_non_required_valid_arguments(self, raise_exception=False):
        return {k: v for k, v in self.get_allowed_arguments().items() if not k in self.required_arugments[self.request.method]}

    def _handle_request_exception(self, e: BaseException) -> None:
        """customized exception handling for localized messages and debug mode"""

        # convert util warning exception to HostrayWebFinish
        if issubclass(type(e), LocalizedMessageWarning):
            try:
                raise HostrayWebFinish(e.code, *e.code_args) from e
            except Exception as exc:
                e = exc

        # log to controller's log
        if not isinstance(e, HostrayWebFinish):
            self.log_error(traceback.format_exc())

        # handle tornado origin exceptions
        return RequestHandler._handle_request_exception(self, e)
