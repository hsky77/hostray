# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
This module defines the base Controller classes

Last Updated:  Monday, 4th November 2019 by hsky77 (howardlkung@gmail.com)
'''

from typing import Union, Callable, Any, List, Dict
from requests import Response

from tornado.web import Finish, RequestHandler

from ... import Module_Path
from ...util import DynamicClassEnum, HostrayLogger, join_path

from .. import HostrayWebException, Controller_Module_Folder, HostrayWebFinish
from ..component import DefaultComponentTypes, OptionalComponentTypes, ComponentManager
from ..component.optional_component import ServicesComponent
from ..component.default_component import CallbackComponent, LocalizationComponent


class ControllerType(DynamicClassEnum):
    """base abstract controller enum class"""
    @staticmethod
    def get_controller_enum_class() -> List[DynamicClassEnum]:
        try:
            return DynamicClassEnum.get_dynamic_class_enum_class(Controller_Module_Folder)
        except:
            pass

    def import_class(self):
        return super().import_class(cls_type=RequestHandler)


class ControllerAddon():
    """contains hostray controller helper functions and variables"""

    def __init__(self, application, request,  **kwds):
        from ..server import HostrayApplication
        self.application: HostrayApplication = application
        self.component_manager: ComponentManager = self.application.component_manager
        self.root_dir: str = self.application.settings['root_dir']
        self.debug: bool = self.application.settings['debug']

        # init server component variables
        self.logger: HostrayLogger = None
        self.services: ServicesComponent = None
        self.callbacks: CallbackComponent = self.component_manager.get_component(
            DefaultComponentTypes.Callback)

    def get_localization_language(self):
        return self.component_manager.get_component(DefaultComponentTypes.Localization).current_language

    def get_localized_message(self, code: Union[str, int], *args) -> str:
        return self.application.get_localized_message(code, *args)

    async def run_method_async(self, func: Callable, *args, pool_id: str = 'default', **kwargs) -> Any:
        return await self.application.run_method_async(func, *args, pool_id=pool_id, **kwargs)

    def log_info(self, msg: str, *args, exc_info=None, extra=None, stack_info=False) -> None:
        if self.logger is None:
            self.logger = self.application.get_logger(type(self).__name__)
        self.application.run_method_in_queue(
            self.logger.info, msg, *args, exc_info=exc_info, extra=extra, stack_info=stack_info)

    def log_warning(self, msg: str, *args, exc_info=None, extra=None, stack_info=False) -> None:
        if self.logger is None:
            self.logger = self.application.get_logger(type(self).__name__)
        self.application.run_method_in_queue(
            self.logger.warning, msg, *args, exc_info=exc_info, extra=extra, stack_info=stack_info)

    def log_error(self, msg: str, *args, exc_info=None, extra=None, stack_info=False) -> None:
        if self.logger is None:
            self.logger = self.application.get_logger(type(self).__name__)
        self.application.run_method_in_queue(
            self.logger.error, msg, *args, exc_info=exc_info, extra=extra, stack_info=stack_info)

    async def invoke_service_async(self, service_name: str, method: str = 'get', route_input: str = '', streaming_callback: Callable = None, **kwargs) -> Response:
        if self.services is None:
            self.services = self.component_manager.get_component(
                OptionalComponentTypes.Service)
        return await self.services.invoke_async(service_name, method=method, route_input=route_input, streaming_callback=streaming_callback, **kwargs)
