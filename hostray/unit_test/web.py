# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Tuesday, 12th November 2019 by hsky77 (howardlkung@gmail.com)
'''

import time
import asyncio

from ..web import Component_Module_Folder, Controller_Module_Folder
from .base import UnitTestCase

root_setting = {'name': 'hostray UT Server Config',
                'port': 58564,
                'debug': True,
                'cookie_secret': 'test-secret',
                # 'ssl': {
                #     'crt': 'crt.crt',
                #     'key': 'key.key'}
                }

component_setting = {
    'localization': {'dir': None},
    'logger': {'dir': 'files/logs', 'log_to_resource': False},
    'worker_pool': {'default': 2},
    'task_queue': {'worker_count': 3},
    'memory_cache': {'sess_lifetime': 600},
    'orm_db': {
        'db_0': {
            'module': 'sqlite_memory',
            'worker': 1,
            'connection_refresh': 60
        }
    },
    'services':
    {
        'https://www.google.com':
        {
            '/': {
                'name': 'test_www',
                        'get': None
            },
        },
        'http://localhost:58564':
        {

            '/alive': {
                'name': 'check_alive', 'get': None
            },
            '/info': {
                'name': 'get_sys_info', 'get': None
            },
            '/test_api': {
                'name': 'test_api',
                'get': None,
                'post': ['value'],
                'put': ['value'],
                'delete': ['id']
            },
            '/test_orm': {
                'name': 'test_orm',
                'get': None,
                'post': ['id', 'name', 'age', 'gender'],
                'put': ['name', 'age', 'gender'],
                'patch': ['id', 'note', 'schedule'],
                'delete': ['id']
            }

        }
    }
}

controller_setting = {
    '/test_api': {
        'enum': 'test_api'},
    '/test_orm': {
        'enum': 'test_orm',
        'params': {
                'use_orm_db': 'db_0'
        }
    },
    '/test_download': {
        'enum': 'test_download'
    },
    '/test_socket': {
        'enum': 'test_socket'
    },
    '/test_file_upload': {
        'enum': 'test_file_upload',
        'params': {
            'upload_dir': 'files'}
    },
    '/test_bytes_upload': {
        'enum': 'test_bytes_upload'
    },
    '/alive': {
        'enum': 'server_alive'
    },
    '/info': {
        'enum': 'components_info'
    }
}

config = root_setting.copy()
config['debug'] = False
config[Component_Module_Folder] = component_setting
config[Controller_Module_Folder] = controller_setting


class WebTestCase(UnitTestCase):
    def test(self):
        self.test_config()
        self.test_components()
        self.test_server_and_controllers()

    def test_config(self):
        from ..web.config_validator import (HostrayWebConfigComponentValidator, HostrayWebConfigControllerValidator,
                                            HostrayWebConfigRootValidator, HostrayWebConfigValidator)

        config = HostrayWebConfigComponentValidator(component_setting)
        self.assertEqual(config.get_parameter(
            'orm_db.db_0.module'), 'sqlite_memory')

        HostrayWebConfigControllerValidator(controller_setting)
        HostrayWebConfigRootValidator(root_setting)

        root_setting[HostrayWebConfigComponentValidator.__name__] = component_setting
        root_setting[HostrayWebConfigControllerValidator.__name__] = controller_setting

        config = HostrayWebConfigValidator(root_setting)
        self.assertEqual(config.get_parameter(
            'component.orm_db.db_0.module'), 'sqlite_memory')

    def test_components(self):
        import os
        from ..web.component import create_server_component_manager, DefaultComponentTypes, OptionalComponentTypes
        from ..web.component.default_component import LocalizationComponent, LoggerComponent, CallbackComponent, WorkerPoolComponent, TaskQueueComponent
        from ..web.component.optional_component import OrmDBComponent, MemoryCacheComponent, ServicesComponent
        from .. import Module_Path
        from ..util import join_path
        dir_path = join_path(Module_Path, 'web')

        component_manager = create_server_component_manager(
            component_setting, dir_path)

        self.test_func_runned = False

        try:
            # test default components:
            # localization
            local: LocalizationComponent = component_manager.get_component(
                DefaultComponentTypes.Localization)
            local.set_language('en')
            self.assertEqual(local.get_message(100), 'stopping application')

            # log
            log: LoggerComponent = component_manager.get_component(
                DefaultComponentTypes.Logger)
            logger = log.get_logger('test_logger')
            logger.info('Test Message')
            for path in log.default_loggers + ['test_logger']:
                path = join_path(dir_path, 'files', 'logs', path + '.log')
                self.assertFalse(os.path.isfile(path))

            # callback
            from .util import UtilTestCase, TestCallbackType
            callbacks: CallbackComponent = component_manager.get_component(
                DefaultComponentTypes.Callback)
            UtilTestCase.test_callback(
                self, callbacks.get_callback_obj(TestCallbackType))

            # worker pool
            pool: WorkerPoolComponent = component_manager.get_component(
                DefaultComponentTypes.WorkerPool)
            pool.run_method(UtilTestCase.test_func, self, 1, kwindex=2)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(pool.run_method_async(
                UtilTestCase.test_func, self, 1, kwindex=2))

            # queued tasks
            queue: TaskQueueComponent = component_manager.get_component(
                DefaultComponentTypes.TaskQueue)

            def test_func(result):
                self.test_func_runned = True

            queue.run_method_in_queue(UtilTestCase.test_func, self, 1,
                                      kwindex=2, on_finish=test_func)

            # test optional components:
            # memory cache
            mem_cache: MemoryCacheComponent = component_manager.get_component(
                OptionalComponentTypes.MemoryCache)
            cache, id = mem_cache.get()
            cache['test_number'] = 1
            cache, id = mem_cache.get(id)
            old_dt = mem_cache.get_expired_datetime(id)
            self.assertTrue(cache['test_number'], 1)
            new_dt = mem_cache.get_expired_datetime(id)
            self.assertEqual(old_dt, new_dt)
            time.sleep(0.1)  # wait for time changed
            cache, new_id = mem_cache.get(
                id, renew_lifetime=True, renew_id=True)
            self.assertNotEqual(id, new_id)
            self.assertTrue(cache['test_number'], 1)
            new_dt = mem_cache.get_expired_datetime(new_id)
            self.assertNotEqual(old_dt, new_dt)
            cache, id = mem_cache.get('123')
            self.assertTrue(not 'test_number' in cache)

            # orm
            from .util_orm import OrmTestCase, GenderType, TestEntity, TestAccessor, DeclarativeBase
            db_id = 'db_0'
            pool: OrmDBComponent = component_manager.get_component(
                OptionalComponentTypes.OrmDB)
            pool.init_db_declarative_base(db_id, DeclarativeBase)
            OrmTestCase.do_test_pool(self, pool.get_pool_obj(db_id))

            # services
            services: ServicesComponent = component_manager.get_component(
                OptionalComponentTypes.Service)
            response = services.invoke('test_www')
            self.assertEqual(response.status_code, 200)

        finally:
            # queue will run at this moment if this test runs too fast
            loop.run_until_complete(
                component_manager.boardcast_async('dispose', component_manager))
            self.assertTrue(self.test_func_runned)

    def test_server_and_controllers(self):
        from .. import Module_Path
        from ..util import join_path, Worker
        from ..web.server import HostrayServer
        from ..web.config_validator import HostrayWebConfigValidator
        from ..web.component import OptionalComponentTypes, create_server_component_manager
        from ..web.component.optional_component import ServicesComponent

        dir_path = join_path(Module_Path, 'web')
        HostrayWebConfigValidator(config)
        server = HostrayServer()

        component_manager = create_server_component_manager(
            component_setting, dir_path)

        with Worker('server_thread') as w:
            try:
                self.server_init_exception = None

                def on_worker_exception(e: Exception):
                    self.server_init_exception = e

                w.run_method(self.start_server, server,
                             dir_path, on_exception=on_worker_exception)

                service: ServicesComponent = component_manager.get_component(
                    OptionalComponentTypes.Service)

                response = None
                while response is None or not response.status_code == 200:
                    if self.server_init_exception:
                        raise self.server_init_exception
                    try:
                        response = service.invoke('check_alive')
                    except:
                        time.sleep(0.5)

                # test request
                response = service.invoke('test_api')
                self.assertEqual(response.status_code, 200)

                # test orm
                response = service.invoke('test_orm', 'get', id=3)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.text, '')

                response = service.invoke(
                    'test_orm', 'post', id=3, name='someone', age=22, gender='male')
                self.assertEqual(response.status_code, 200)

                response = service.invoke(
                    'test_orm', 'put', name='someone', age=22, gender='males')
                self.assertEqual(response.status_code, 200)

                response = service.invoke(
                    'test_orm', 'patch', id=3, note='this is note', schedule='2019-11-05 15:06:41.606609')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.text, 'This page is expired, please refresh pages')

                response = service.invoke('test_orm', 'get', id=3)
                self.assertEqual(response.status_code, 200)
                self.assertNotEqual(response.text, '')

                response = service.invoke('test_orm', 'patch', cookies=response.cookies,
                                          id=3, note='this is note', schedule='2019-11-05 15:06:41.606609')
                self.assertEqual(response.status_code, 200)
                self.assertNotEqual(
                    response.text, 'This page is expired, please refresh pages')

                response = service.invoke(
                    'test_orm', 'delete', cookies=response.cookies, id=3)
                self.assertEqual(response.status_code, 200)

                response = service.invoke('test_orm', 'get', id=3)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.text, '')

                # test bytes upload
                from ..web.client import StreamUploadClient
                with StreamUploadClient() as client:
                    response = client.send_bytes(
                        'http://localhost:58564/test_bytes_upload', b'i am bytes')
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.text, 'i am bytes')

                # test web socket
                from ..web.client import WebSocketClient
                with WebSocketClient() as client:
                    self.received_msg = None

                    def received_ws_msg(msg):
                        self.received_msg = msg

                    client.connect('ws://localhost:58564/test_socket',
                                   on_message_callback=received_ws_msg)
                    client.write_message('Hello There')

                    while self.received_msg is None:  # wait for message come back
                        time.sleep(0)

                    self.assertEqual(self.received_msg, 'Hello There')

            finally:
                server.stop()
                while w.is_func_running:  # wait for server stoped
                    pass
                loop = asyncio.get_event_loop()
                loop.run_until_complete(
                    component_manager.boardcast_async('dispose', component_manager))

    def start_server(self, server, dir_path: str):
        from tornado.ioloop import IOLoop
        from ..web.component import DefaultComponentTypes
        from ..web.component.default_component import LocalizationComponent
        IOLoop().make_current()
        server.init(dir_path, config=config)

        local: LocalizationComponent = server.app.component_manager.get_component(
            DefaultComponentTypes.Localization)
        local.set_language('en')

        server.start()
