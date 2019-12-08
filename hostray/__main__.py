# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Thursday, 7th November 2019 by hsky77 (howardlkung@gmail.com)
'''

import os
import sys
from .util import get_class, join_path
from . import Module_Path


def start_server(server_dir: str, cmdline_args) -> None:
    from .util import get_class

    try:
        route = server_dir + '.server'
        cls = server_dir + '_server'
        server_cls = get_class(route, cls)
    except:
        from .web.server import HostrayServer
        server_cls = HostrayServer

    server = server_cls()
    server.init(server_dir, cmdline_args.http_server)
    server.start()


def pack_server(server_dir: str, cmdline_args) -> None:
    from .web.pack import HostrayPack
    HostrayPack().pack(server_dir, cmdline_args.o,
                       prepare_wheels=cmdline_args.add_wheels,
                       compile_py=not cmdline_args.decompile_pyc)


def test_server():
    import unittest
    from .unit_test import get_test_suite
    runner = unittest.TextTestRunner()
    runner.run(get_test_suite())


def create_server_folder(server_dir: str = 'hello_world'):
    from .web import (Component_Module_Folder,
                      Controller_Module_Folder,
                      Unittest_Module_Folder,
                      Hostray_Web_Config_File,
                      Hostray_Web_Pack_File,
                      Component_Module_Folder,
                      Controller_Module_Folder,
                      Hostray_Web_Requirement_File)
    from .web.server import HostrayServer

    if not os.path.isdir(server_dir):
        os.makedirs(server_dir)

    # create hello component
    comp_dir = join_path(server_dir, Component_Module_Folder)
    if not os.path.isdir(comp_dir):
        os.makedirs(comp_dir)

    with open(join_path(comp_dir, '__init__.py'), 'w') as f:
        f.write('''\
from hostray.web.component import ComponentTypes

class HelloComponentTypes(ComponentTypes):
    Hello = ('hello', 'hello', 'HelloComponent')
''')

    with open(join_path(comp_dir, 'hello.py'), 'w') as f:
        f.write('''\
from hostray.web.component import Component
from . import HelloComponentTypes

class HelloComponent(Component):
    def init(self, component_manager, *arugs, **kwargs) -> None:
        print('init Hello component load from', __package__)

    def hello(self):
        return 'Hello World, This is hostray generate hello component'
''')

    # create hello controller
    controller_dir = join_path(server_dir, Controller_Module_Folder)
    if not os.path.isdir(controller_dir):
        os.makedirs(controller_dir)

    with open(join_path(controller_dir, '__init__.py'), 'w') as f:
        f.write('''\
from hostray.web.controller import ControllerType

class HelloControllerTypes(ControllerType):
    HelloController = ('hello_world', 'hello', 'HelloController')
    THelloController = ('tornado_hello_world', 'hello', 'HelloTornadoHandler')
''')

    with open(join_path(controller_dir, 'hello.py'), 'w') as f:
        f.write('''\
from hostray.web.controller import RequestController

from component import HelloComponentTypes

class HelloController(RequestController):
    async def get(self):
        hello_comp = self.component_manager.get_component(HelloComponentTypes.Hello)
        self.write(hello_comp.hello())

from tornado.web import RequestHandler

class HelloTornadoHandler(RequestHandler):
    async def get(self):
        hello_comp = self.application.component_manager.get_component(HelloComponentTypes.Hello)
        self.write(hello_comp.hello())
''')

    # unit test
    ut_dir = join_path(server_dir, Unittest_Module_Folder)
    if not os.path.isdir(ut_dir):
        os.makedirs(ut_dir)

    with open(join_path(ut_dir, '__init__.py'), 'w') as f:
        f.write('''\
from hostray.unit_test import UnitTestTypes

class UTTypes(UnitTestTypes):
    UT1 = ('ut1', 'ut1', 'UT1TestCase')
''')

    with open(join_path(ut_dir, 'ut1.py'), 'w') as f:
        f.write('''\
from hostray.unit_test import UnitTestCase

class UT1TestCase(UnitTestCase):
    def test(self):
        # implement unit test here...
        
        print('ut1 test case runned')
''')

    # config
    with open(join_path(server_dir, Hostray_Web_Config_File), 'w') as f:
        f.write('''\
name: hostray Server
port: 8888
debug: False
component:
  hello: 
controller:
  /hello:
    enum: hello_world
  /hello_tornado:
    enum: tornado_hello_world
''')

    # pack
    with open(join_path(server_dir, Hostray_Web_Pack_File), 'w') as f:
        f.write('''
# this is packing list indicated what are the files should be pack
# if this file does not exist under the project folder, all of the files under the folder will be packed

include:
# if include is not specfied, only collect all of the files under the server folder
# list absolute or relative path of file or directory
# - example.txt
# - example_dir

exclude:
# if exclude is not specfied, keeps all of the files
# list absolute or relative path of file, directory, or file extension
- '.log'
''')

    # requirement
    from . import __name__, Version
    with open(join_path(server_dir, Hostray_Web_Requirement_File), 'w') as f:
        f.write('{}>={}'.format(__name__, Version))

    print('project created at', os.path.abspath(server_dir))


Command_Start_Server = 'start'
Command_Pack_Server = 'pack'
Command_Test_Server = 'test'
Command_Create_Project = 'create'


def get_command_parser():
    import argparse
    parser = argparse.ArgumentParser(prog='hostray')
    sub_parsers = parser.add_subparsers(title='command')

    start_parser = sub_parsers.add_parser(
        Command_Start_Server, help='start server with specfied directory path')
    start_parser.add_argument('server_directory',
                              help='server directory path')
    start_parser.add_argument('-s', '--http_server', action='store_true',
                              help='start application on tornado http server')
    start_parser.set_defaults(command=Command_Start_Server)

    pack_parser = sub_parsers.add_parser(
        Command_Pack_Server, help='pack server with specfied directory path')
    pack_parser.add_argument('server_directory',
                             help='server directory path')
    pack_parser.add_argument(
        '-o', help='specify output compressed file path', default=None)
    pack_parser.add_argument('-w', '--add_wheels', action='store_true',
                             help='add dependency wheel files')
    pack_parser.add_argument('-d', '--decompile_pyc', action='store_true',
                             help='disable compile .py to .pyc')
    pack_parser.set_defaults(command=Command_Pack_Server)

    test_parser = sub_parsers.add_parser(
        Command_Test_Server, help='test hostray library or specfied server path')
    test_parser.add_argument('server_directory', nargs='?',
                             help='server directory path')
    test_parser.set_defaults(command=Command_Test_Server)

    make_serv_parser = sub_parsers.add_parser(
        Command_Create_Project, help='create a server template with specfied directory path')
    make_serv_parser.add_argument('server_directory',
                                  help='server directory path')
    make_serv_parser.set_defaults(command=Command_Create_Project)

    return parser


def _init_server_package(server_dir: str) -> None:
    if server_dir is not None:
        if not join_path(Module_Path) in server_dir and not server_dir in sys.path:
            sys.path.append(os.path.abspath(server_dir))

        from .util import get_class
        from .web import Component_Module_Folder, Controller_Module_Folder, Unittest_Module_Folder
        try:
            get_class(Component_Module_Folder)
        except:
            pass

        try:
            get_class(Controller_Module_Folder)
        except:
            pass

        try:
            get_class(Unittest_Module_Folder)
        except:
            pass


if __name__ == '__main__':
    parser = get_command_parser()
    args = parser.parse_args()

    if hasattr(args, 'command'):
        if args.command == Command_Start_Server:
            server_dir = args.server_directory
            _init_server_package(server_dir)
            start_server(server_dir, args)
        elif args.command == Command_Pack_Server:
            from .util import join_to_abs_path
            pack_server(join_to_abs_path(args.server_directory), args)
        elif args.command == Command_Test_Server:
            server_dir = args.server_directory
            _init_server_package(server_dir)
            test_server()
        elif args.command == Command_Create_Project:
            create_server_folder(args.server_directory)
        else:
            parser.print_help()
    else:
        parser.print_help()
