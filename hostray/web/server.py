# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Monday, 4th November 2019 by hsky77 (howardlkung@gmail.com)
'''


import os
from typing import List, Any, Callable, Awaitable, Dict, Union
from tornado.web import Application


from hostray.util import join_path, HostrayLogger, DynamicClassEnum, join_to_abs_path
from .component import (ComponentManager, ComponentTypes, DefaultComponentTypes,
                        OptionalComponentTypes, create_server_component_manager)

from .controller import ControllerType, get_controllers

from . import (HostrayWebException, LocalCode_Application_Closing, LocalCode_File_Not_Found,
               LocalCode_Application_Closed, Component_Module_Folder,
               Hostray_Web_Config_File, Controller_Module_Folder)


class HostrayApplication(Application):
    def init(self):
        import threading
        from logging import getLogger
        self.do_close = False
        self.exiting = False

        if threading.current_thread() is threading.main_thread():
            import signal
            signal.signal(signal.SIGINT, self.signal_handler)

        if Component_Module_Folder in self.settings:
            self.component_manager = create_server_component_manager(
                self.settings[Component_Module_Folder],
                self.settings['root_dir'])
        else:
            # default component manager
            self.component_manager = create_server_component_manager(
                None, self.settings['root_dir'])

        self.component_manager.invoke(
            DefaultComponentTypes.Logger, 'set_default_logger_echo', self.settings['debug'])

        self.logger: HostrayLogger = getLogger('tornado.application')

    def signal_handler(self, signum, frame):
        self.exit()

    def exit(self):
        self.logger.info(self.get_localized_message(
            LocalCode_Application_Closing))
        self.do_close = True

    async def do_exit(self):
        if self.do_close:
            if not self.exiting:
                self.exiting = True
                await self.component_manager.dispose_components()
                from tornado.ioloop import IOLoop
                IOLoop.current().stop()
                self.logger.info(self.get_localized_message(
                    LocalCode_Application_Closed))

    def get_localized_message(self, code: Union[str, int], *arugs) -> str:
        return self.component_manager.get_component(DefaultComponentTypes.Localization).get_message(str(code), *arugs)

    def get_logger(self, name: str, sub_dir: str = '', mode: str = 'a', encoding: str = 'utf-8') -> HostrayLogger:
        return self.component_manager.get_component(DefaultComponentTypes.Logger).get_logger(name, sub_dir, mode, encoding)

    def run_method_in_queue(self, func: Callable, *args, on_finish: Callable[[Any], None] = None, on_exception: Callable[[Exception], None] = None,
                            **kwargs):
        self.component_manager.get_component(DefaultComponentTypes.TaskQueue).run_method_in_queue(
            func, *args, on_finish=on_finish, on_exception=on_exception, **kwargs)

    async def run_method_async(self, func: Callable, *args, pool_id: str = 'default', **kwargs) -> Any:
        return await self.component_manager.get_component(DefaultComponentTypes.WorkerPool).run_method_async(func, *args, pool_id=pool_id, **kwargs)


class HostrayServer():
    def start(self):
        from tornado.ioloop import IOLoop, PeriodicCallback
        PeriodicCallback(self.app.do_exit, 1000).start()
        IOLoop.current().start()

    def stop(self):
        if self.app:
            self.app.exit()

    def start_periodic_callback(self, awaitable_func: Awaitable, *args, interval: int = 1000, **kwargs) -> None:
        from tornado.ioloop import PeriodicCallback
        from inspect import iscoroutinefunction
        if iscoroutinefunction(awaitable_func):
            PeriodicCallback(lambda: self.__periodic_callback_decorator(
                awaitable_func, *args, **kwargs), interval).start()

    async def __periodic_callback_decorator(self, func, *args, **kwargs):
        if not self.app.exiting:
            await func(*args, **kwargs)

    def init(self, server_dir: str, use_http_server: bool = False, config: Dict = None, **kwargs) -> None:
        self.root_dir = join_to_abs_path(server_dir)
        self.config_path = join_to_abs_path(
            server_dir, Hostray_Web_Config_File)

        if config:
            self.config = config
            self.config_path = None
        else:
            with open(self.config_path, 'r') as f:
                import yaml
                from .config_validator import HostrayWebConfigValidator
                validator = HostrayWebConfigValidator(
                    yaml.load(f, Loader=yaml.SafeLoader))
                self.config = validator.parameter

        self._make_app()

        if use_http_server or 'ssl' in self.config:
            from tornado.web import HTTPServer

            if 'ssl' in self.config:
                if not os.path.isfile(join_path(self.config['ssl']['crt'])):
                    raise HostrayWebException(
                        LocalCode_File_Not_Found, join_path(self.config['ssl']['crt']))
                if not os.path.isfile(join_path(self.config['ssl']['key'])):
                    raise HostrayWebException(
                        LocalCode_File_Not_Found, join_path(self.config['ssl']['key']))

                import ssl
                ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ssl_ctx.load_cert_chain(join_path(self.config['ssl']['crt']),
                                        join_path(self.config['ssl']['key']))
                if 'ca' in self.config['ssl']:
                    if not os.path.isfile(join_path(self.config['ssl']['ca'])):
                        raise HostrayWebException(
                            LocalCode_File_Not_Found, join_path(self.config['ssl']['ca']))
                    ssl_ctx.load_verify_locations(
                        join_path(self.config['ssl']['ca']))

                self.server = HTTPServer(self.app, ssl_options=ssl_ctx)
            else:
                self.server = HTTPServer(self.app)

            self.server.listen(self.config['port'])
        else:
            self.app.listen(self.config['port'])

    def _make_app(self):
        settings = {
            'root_dir': self.root_dir,
            'config_path': self.config_path,
            **self.config
        }

        controllers, settings = get_controllers(settings, self.root_dir)
        self.app = self._make_app_instance(controllers, settings)
        self.app.init()

    def _make_app_instance(self, controllers, settings):
        return HostrayApplication(controllers, **settings)
