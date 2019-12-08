# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
This module contains the "yaml" configurable controller classes for hostray application.

    - to create and setup controller api:

        0. the hierarchy of folders and files looks like:

            server_directory/
                server_config.yaml
                controller/
                    __init__.py
                    foo.py

        1. "__init__.py" defines the controllers:
            from hostray.web.controller import ControllerType

            class ExControllerType(ControllerType):
                Foo = ('foo', 'foo', 'Foo')

        2. "foo.py" contains the controller class:

            from hostray.web.controller import RequestController

            class Foo(RequestController):

                def initialize(self, p1, **kwds):
                    self.p1 = p1

                async def get(self):
                    self.write('Hello Workd: ', self.p1)

        3. setup component block of "server_config.yaml" to tell hostray server load the extend components "Foo":

            controller:                 # block to setup controllers
                /foo:                   # api route
                    enum: foo           # tells to load foo controller class
                    params:
                        p1: xxxx        # parameter p1 of Foo.initialize()

Last Updated:  Tuesday, 5th November 2019 by hsky77 (howardlkung@gmail.com)
'''

from typing import List, Dict

from .. import HostrayWebException, LocalCode_Failed_To_Load_Controller

from ...util import join_path
from .base import ControllerType
from .request_controller import RequestController, RESTfulMethodType
from .web_socket_controller import WebSocketController
from .db_cusd_controller import DBCSUDController
from .streaming_controller import StreamingUploadController, StreamingDownloadController, StreamingFileUploadController


class DefaultControllerType(ControllerType):
    Frontend = ('frontend', 'tornado.web', 'StaticFileHandler')
    SystemAlive = ('server_alive', 'default_controller',
                   'SystemAliveController')
    ComponentsInfo = ('components_info', 'default_controller', 'ComponentsInfoController')


class UnitTestControllerType(ControllerType):
    TestController = (
        'test_api', 'unittest_controller', 'TestController'
    )

    TestCUSDController = (
        'test_orm', 'unittest_controller', 'TestCUSDController'
    )

    TestStreamDownloadController = (
        'test_download', 'unittest_controller', 'TestStreamDownloadController'
    )

    TestWebsocketController = (
        'test_socket', 'unittest_controller', 'TestWebsocketController'
    )

    TestStreamFileUploadController = (
        'test_file_upload', 'hostray.web.controller', 'StreamingFileUploadController'
    )

    TestStreamUploadController = (
        'test_bytes_upload', 'unittest_controller', 'TestStreamUploadController'
    )


def _get_controller_enum(key: str, contoller_types: List[ControllerType]):
    for contoller_type in contoller_types:
        try:
            return contoller_type(key).import_class()
        except:
            continue


def get_controllers(server_setting: Dict, server_dir: str = None) -> List:
    from tornado.web import StaticFileHandler
    from .. import Controller_Module_Folder
    controllers = []
    if Controller_Module_Folder in server_setting and isinstance(server_setting[Controller_Module_Folder], dict):
        contoller_types = [DefaultControllerType, UnitTestControllerType]
        try:
            extend_controller_type = ControllerType.get_controller_enum_class()
            contoller_types = extend_controller_type + \
                contoller_types if extend_controller_type else contoller_types
        except:
            pass

        for path, v in server_setting[Controller_Module_Folder].items():
            if 'enum' in v:
                cls_type = _get_controller_enum(v['enum'], contoller_types)
                if cls_type is None:
                    raise HostrayWebException(
                        LocalCode_Failed_To_Load_Controller, server_dir, v['enum'])

                params = v['params'] if 'params' in v and v['params'] is not None else {}
                if issubclass(cls_type, StaticFileHandler):
                    server_setting['static_handler_class'] = cls_type
                    if 'path' in params:
                        params['path'] = join_path(server_dir, params['path'])

                controllers.append((path, cls_type, params))

    return controllers, server_setting
