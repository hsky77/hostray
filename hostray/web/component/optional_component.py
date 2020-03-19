# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
build-in optional components in hostray.web.component.OptionalComponentTypes,
hostray application loads the components if server_config.yaml specified

    MemoryCacheComponent:

        - web server session(server-side cache) by server config as followings:

        component:                          # component block of server_config.yaml
            memory_cache:                   # indicate DefaultComponentTypes.MemoryCache
                sess_lifetime: <int>        # required - session life time in seconds
                renew_lifetime: <bool>      # optional - renew session life time when access session
                # optional - renew session id when access session (One-Time Access)
                renew_id: <bool>
                # optional - file path to store and recover sessions.
                save_file: <str>
                                            #   sessions won't be saved if save_file is not specified

    OrmDBComponent:

        - managing sql database connection and access with server config as followings:

        note:
            OrmDBComponent holds database connection, database might cut off the connections for long time idles,
            so it's necessary to refresh connection by calling reset_session() or reset_session_async() before query database,
            parameter "connection_refresh" is the timer to prevent rapidly reconnect database

        component:                                  # component block of server_config.yaml
            orm_db:                                 # indicate DefaultComponentTypes.OrmDB
                db_id_1:    <str>                   # define string id will be use in code
                    module: <str>                   # required - support 'sqlite', 'sqlite_memory', 'mysql'
                    worker: <int>                   # optional - db access worker limit, default 1
                    connection_refresh: <int>       # optional - timer to refresh connection, default 30 seconds

                    # when module is 'sqlite', you should add parameters:
                    file_name: <str>                # required - specify sqlite db file path

                    # when module is 'mysql', you should add parameters:
                    host:       <str>               # required - db ip
                    port:       <int>               # required - db port
                    db_name:    <str>               # required - db database name
                    user:       <str>               # required - login user id
                    password:   <str>               # required - login user password
                db_id_2:
                    ...etc

    ServicesComponent:

        - managing hostray customized http request client with server config as followings:

        component:
            services:
                url:                        <str>
                    /api:                   <str>
                        name:               <str>
                        # required: 'get', 'post', 'put', 'delete', 'patch', 'option'
                        method:             <str>

                            # optional: the sending requests only contain the specified argument names, if not, contains every argument
                            - arg_name_1:   <str>
                            - arg_name_2:   <str>
                            - etc...

                    /api:
                        etc...

                url:
                    etc...

Last Updated:  Tuesday, 5th November 2019 by hsky77 (howardlkung@gmail.com)
'''

import asyncio
import time
from enum import Enum
from typing import Union, Callable, Dict, Tuple, Any, List, Awaitable
from datetime import datetime, timedelta
from contextlib import contextmanager
from requests import Response

from aiohttp import request, ClientResponse, TCPConnector, ClientSession
from hostray.util import generate_base64_uid, join_path, asynccontextmanager
from hostray.util.orm import OrmAccessWorkerPool, DB_MODULE_NAME, DeclarativeMeta

from .. import (HostrayWebException, LocalCode_Not_Accessor_Function,
                LocalCode_No_DB_Module, LocalCode_Not_Support_DB_Module)

from . import Component, OptionalComponentTypes, ComponentManager, DefaultComponentTypes
from .default_component import WorkerPoolComponent


class MemoryCacheComponent(Component):
    """optional component for web server session(server-side cache) by server config"""
    KEY_EXPIRED = 'expired'
    KEY_SESSION = 'session'

    def info(self) -> Dict:
        return {**super().info(), **{'info': {
            'sess_lifetime': self.sess_lifetime,
            'renew_lifetime': self.renew_lifetime,
            'renew_id': self.renew_id
        }}}

    def init(self, component_manager: ComponentManager, sess_lifetime: int, **kwargs) -> None:
        self.dict = {}
        self.sess_lifetime = sess_lifetime
        self.save_file = kwargs.get('save_file', None)
        if self.save_file is not None:
            self.save_file = join_path(
                kwargs.get('root_dir', ''), self.save_file)

        self.renew_lifetime = kwargs.get('renew_lifetime', False)
        self.renew_id = kwargs.get('renew_id', False)

        self.load_from_file()

    def get_expired_datetime(self, session_id: str) -> datetime:
        return self.dict[session_id][self.KEY_EXPIRED] if session_id in self.dict else datetime.now()

    def get(self, session_id: str = '', renew_lifetime: bool = False, renew_id: bool = False) -> Tuple[dict, str]:
        """return an non expired or new session dict and id"""
        if self.__is_session_valid(session_id):
            if renew_id or self.renew_id:
                id = generate_base64_uid()
                self.dict[id] = self.dict[session_id]
                del self.dict[session_id]
                session_id = id

            if renew_lifetime or self.renew_lifetime:
                self.dict[session_id] = self.__create_new_session(
                    self.dict[session_id][self.KEY_SESSION])

            return self.dict[session_id][self.KEY_SESSION], session_id
        else:
            session_id = generate_base64_uid()
            self.dict[session_id] = self.__create_new_session(data={})
            return self.dict[session_id][self.KEY_SESSION], session_id

    def save_to_file(self) -> None:
        import pickle
        import os
        if self.save_file is not None:
            if not os.path.isdir(os.path.dirname(self.save_file)):
                os.makedirs(os.path.dirname(self.save_file))
            with open(self.save_file, 'wb') as f:
                pickle.dump(self.dict, f)

    def load_from_file(self) -> None:
        import pickle
        import os
        if self.save_file is not None:
            if os.path.isfile(self.save_file):
                with open(self.save_file, 'rb') as f:
                    self.dict = pickle.load(f)

    def clear_session(self, session_id: str) -> None:
        if not session_id in self.dict:
            del self.dict[session_id]

    def __create_new_session(self, data):
        sess = {
            self.KEY_EXPIRED: datetime.now() + timedelta(seconds=self.sess_lifetime),
            self.KEY_SESSION: data
        }
        return sess

    def __is_session_valid(self, session_id):
        if not session_id in self.dict:
            return False
        else:
            if self.dict[session_id][self.KEY_EXPIRED] >= datetime.now():
                return True
            else:
                del self.dict[session_id]
                return False

    def dispose(self, component_manager: ComponentManager) -> None:
        self.save_to_file()


class OrmDBComponent(Component):
    """
    optional component for managing sql database access with server config

    note: this component object holds db connection, db might cut off the connection for long time idle,
        so it's necessary to refresh connection
    """

    support_db_type = ['sqlite', 'sqlite_memory', 'mysql']

    def init(self, component_manager: ComponentManager, **kwargs) -> None:
        self.root_dir = kwargs.get('root_dir', '')

        self.dbs = {k: v for k, v in kwargs.items() if not 'root_dir' in k}
        for k in self.dbs:
            self.dbs[k]['db'] = None
            self.dbs[k]['reset_dt'] = None
            self.dbs[k]['open'] = False

            self.dbs[k]['worker'] = self.dbs[k].get('worker', 1)
            self.dbs[k]['connection_refresh'] = self.dbs[k].get(
                'connection_refresh', 30)

            if not 'module' in self.dbs[k]:
                if not self.dbs[k]['module'] in self.support_db_type:
                    raise HostrayWebException(
                        LocalCode_Not_Support_DB_Module, k, self.dbs[k]['module'])
                raise HostrayWebException(LocalCode_No_DB_Module)

            if self.dbs[k]['module'] == 'sqlite':
                self.dbs[k]['file_name'] = join_path(
                    self.root_dir, self.dbs[k]['file_name'])

    def info(self) -> Dict:
        res = {}
        for db_id in self.dbs:
            res[db_id] = self.get_db_settings(db_id)
        return {**super().info(), **{'info': res}}

    def get_pool_obj(self, db_id: str) -> OrmAccessWorkerPool:
        return self.dbs[db_id]['db']

    def get_db_settings(self, db_id: str) -> Dict:
        return {k: v for k, v in self.dbs[db_id].items() if not k in ['db']}

    def init_db_declarative_base(self, db_id: str, declared_entity_base: DeclarativeMeta) -> None:
        if db_id in self.dbs:
            if not self.dbs[db_id]['db']:
                db = OrmAccessWorkerPool(
                    pool_name=db_id, worker_limit=self.dbs[db_id]['worker'])

                module = DB_MODULE_NAME.SQLITE_MEMORY
                if self.dbs[db_id]['module'] == 'sqlite':
                    module = DB_MODULE_NAME.SQLITE_FILE
                elif self.dbs[db_id]['module'] == 'mysql':
                    module = DB_MODULE_NAME.MYSQL

                db.set_session_maker(
                    module, declared_entity_base, **self.dbs[db_id])
                self.dbs[db_id]['reset_dt'] = None
                self.dbs[db_id]['db'] = db
                self.dbs[db_id]['open'] = True

    @contextmanager
    def reserve_worker(self, db_id: str) -> str:
        with self.dbs[db_id]['db'].reserve_worker() as identity:
            yield identity

    @asynccontextmanager
    async def reserve_worker_async(self, db_id: str) -> str:
        async with self.dbs[db_id]['db'].reserve_worker_async() as identity:
            yield identity

    def reset_session(self, db_id: str, force_reconnect: bool = False) -> None:
        """reset db worker sessions

        ATTENTION: do not call this function in the clauses of 'with reserve_worker():' and 'with reserve_worker_async():'
        """
        if self.dbs[db_id]['open'] and not self.dbs[db_id]['module'] == 'sqlite_memory':
            if self.dbs[db_id]['worker'] < 2:
                force_reconnect = False

            if force_reconnect:
                self.dbs[db_id]['db'].reset_connection()
                self.dbs[db_id]['reset_dt'] = datetime.now()
            else:
                if self.dbs[db_id]['reset_dt'] is None:
                    self.dbs[db_id]['reset_dt'] = datetime.now()
                elif (datetime.now() - self.dbs[db_id]['reset_dt']).seconds > self.dbs[db_id]['connection_refresh']:
                    self.dbs[db_id]['reset_dt'] = datetime.now()
                    self.dbs[db_id]['db'].reset_connection()

    async def reset_session_async(self, db_id: str, force_reconnect: bool = False) -> None:
        """reset db worker sessions

        ATTENTION: do not call this function in the clauses of 'with reserve_worker():' and 'with reserve_worker_async():'
        """
        if self.dbs[db_id]['open'] and not self.dbs[db_id]['module'] == 'sqlite_memory':
            if self.dbs[db_id]['worker'] < 2:
                force_reconnect = False

            if force_reconnect:
                await self.dbs[db_id]['db'].reset_connection_async()
                self.dbs[db_id]['reset_dt'] = datetime.now()
            else:
                if self.dbs[db_id]['reset_dt'] is None:
                    self.dbs[db_id]['reset_dt'] = datetime.now()
                elif (datetime.now() - self.dbs[db_id]['reset_dt']).seconds > self.dbs[db_id]['connection_refresh']:
                    await self.dbs[db_id]['db'].reset_connection_async()
                    self.dbs[db_id]['reset_dt'] = datetime.now()

    def run_accessor(self, db_id: str, accessor_func: Callable, *args, identity: str = None, **kwargs) -> Any:
        from hostray.util.orm import OrmDBEntityAccessor
        if issubclass(type(accessor_func.__self__), OrmDBEntityAccessor):
            if self.dbs[db_id]['open']:
                return self.dbs[db_id]['db'].run_method(accessor_func, *args, identity=identity, **kwargs)
        else:
            raise HostrayWebException(
                LocalCode_Not_Accessor_Function, accessor_func)

    async def run_accessor_async(self, db_id: str, accessor_func: Callable, *args, identity: str = None, **kwargs) -> Any:
        from hostray.util.orm import OrmDBEntityAccessor
        if issubclass(type(accessor_func.__self__), OrmDBEntityAccessor):
            if self.dbs[db_id]['open']:
                return await self.dbs[db_id]['db'].run_method_async(accessor_func, *args, identity=identity, **kwargs)
        else:
            raise HostrayWebException(
                LocalCode_Not_Accessor_Function, accessor_func)

    def dispose(self, component_manager: ComponentManager) -> None:
        for db_id in self.dbs:
            if self.dbs[db_id]['open']:
                self.dbs[db_id]['open'] = False
                self.dbs[db_id]['db'].dispose()


class ServicesComponent(Component):
    """optional component for managing hostray customized http request client"""

    class ServiceClient():
        """client to send request"""
        request_methods = [
            'get',
            'post',
            'patch',
            'put',
            'delete',
            'option'
        ]

        request_parameters = [
            # aiohttp request reserved parameters
            'params',
            'headers',
            'timeout',
            'allow_redirects',
            'cert',
            'data',
            'json',
            'cookies',
            'skip_auto_headers',
            'auth',
            'max_redirects',
            'compress',
            'chunked',
            'expect100',
            'raise_for_status',
            'read_until_eof',
            'proxy',
            'proxy_auth',
            'verify_ssl',
            'fingerprint',
            'ssl_context',
            'ssl',
            'proxy_headers',
            'trace_request_ctx'
        ]

        def __init__(self, url_prefix: str = '', config: Dict = None, async_connection_limit: int = 30, async_connection_limit_pre_host: int = 10):
            self.url = url_prefix
            self.params = {}
            if config:
                self.config = {k: v for k,
                               v in config.items() if not 'name' in k}
                self.methods = [
                    k for k in self.request_methods if k in config.keys()]
                if len(self.methods) == 0:
                    self.methods = self.request_methods

                if len(self.methods) > 0:
                    self.params = {k: v for k, v in config.items()
                                   if k in self.request_methods and k not in ['name']}
            else:
                self.methods = self.request_methods

            self.client: ClientSession = None
            self.limit = async_connection_limit
            self.limit_pre_host = async_connection_limit_pre_host

        def set_async_client(self, client: ClientSession = None) -> None:
            if not self.client:
                if not client:
                    self.client = ClientSession(connector=TCPConnector(
                        limit=self.limit, limit_per_host=self.limit_pre_host))
                else:
                    self.client = client

                self.async_methods = {
                    'get': self.client.get,
                    'post': self.client.post,
                    'put': self.client.put,
                    'delete': self.client.delete,
                    'patch': self.client.patch,
                    'head': self.client.head,
                    'options': self.client.options
                }

        def invoke(self,
                   url: str,
                   method: str = 'get',
                   route_input: str = '',
                   streaming_callback: Callable = None,
                   chunk_size: int = 8192,
                   **kwargs) -> Response:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.invoke_async(
                url, method, route_input, streaming_callback, chunk_size, **kwargs))

        async def invoke_async(self,
                               url: str = '',
                               method: str = 'get',
                               route_input: str = '',
                               streaming_callback: Callable = None,
                               chunk_size: int = 8192,
                               **kwargs) -> Response:
            if self.url:
                url = self.url + '/' + route_input if route_input else self.url

            kwargs = self.__parse_parameters(method, **kwargs)

            if method in self.methods:
                result: Response = Response()
                if callable(streaming_callback):
                    async with self.async_methods[method](url, **kwargs) as response:
                        async for chunk in response.content.iter_chunked(chunk_size):
                            streaming_callback(chunk)
                else:
                    async with self.async_methods[method](url, **kwargs) as response:
                        dt = datetime.now()
                        result._content = await response.read()
                        dt = datetime.now() - dt

                result.status_code = response.status
                result.url = str(response.real_url)
                result.headers = {
                    k: v for k, v in response.headers.items()}
                result.cookies = response.cookies
                result.history = response.history
                result.elapsed = dt
                result.encoding = response.get_encoding()
                result.request = response.request_info
                return result

        def __parse_parameters(self, method: str, **kwargs):
            params = {k: v for k, v in kwargs.items()
                      if k not in self.request_parameters}

            if method in self.params and self.params[method]:
                params = {k: v for k, v in kwargs.items()
                          if k in self.params[method]}

            if method in ['get', 'delete']:
                params = {'params': params}
            else:
                params = {'data': params}

            kwargs = {**{k: v for k, v in kwargs.items()
                         if k in self.request_parameters}, **params}

            return kwargs

    def init(self, component_manager: ComponentManager, limit: int = 30, limit_per_host: int = 10,  **kwargs) -> None:
        self.worker_poll: WorkerPoolComponent = component_manager.get_component(
            DefaultComponentTypes.WorkerPool)
        self.services = {}
        self.limit = limit
        self.limit_pre_host = limit_per_host
        self.default_client = ServicesComponent.ServiceClient(
            async_connection_limit=limit, async_connection_limit_pre_host=limit_per_host)
        self.client = None

        for url in kwargs.keys():
            apis = kwargs.get(url)
            if isinstance(apis, dict):
                for api in apis:
                    api_url = url + api
                    self.services[apis[api]['name']] = ServicesComponent.ServiceClient(
                        api_url, apis[api])

    def info(self) -> Dict:
        res = {
            k:
            {
                'url': v.url,
                'methods': v.config
            } for k, v in self.services.items()
        }

        return {**super().info(), **{'info': res}}

    def invoke(self,
               service_name_or_url: str = None,
               method='get',
               route_input: str = '',
               streaming_callback: Callable = None,
               chunk_size: int = 8192,
               **kwargs) -> Response:
        self.__init_client()

        if service_name_or_url in self.services:
            return self.services[service_name_or_url].invoke(None, method, route_input, streaming_callback, chunk_size, **kwargs)
        else:
            return self.default_client.invoke(service_name_or_url, method, route_input, streaming_callback, chunk_size, **kwargs)

    async def invoke_async(self,
                           service_name_or_url: str = None,
                           method='get',
                           route_input: str = '',
                           streaming_callback: Callable = None,
                           chunk_size: int = 8192,
                           **kwargs) -> Response:
        self.__init_client()

        if service_name_or_url in self.services:
            return await self.services[service_name_or_url].invoke_async(None, method, route_input, streaming_callback, chunk_size, **kwargs)
        else:
            return await self.default_client.invoke_async(service_name_or_url, method, route_input, streaming_callback, chunk_size, **kwargs)

    def __init_client(self):
        if not self.client:
            self.client = ClientSession(connector=TCPConnector(
                limit=self.limit, limit_per_host=self.limit_pre_host))
            for _, client in self.services.items():
                client.set_async_client(self.client)
            self.default_client.set_async_client(self.client)

    async def dispose(self, component_manager: ComponentManager):
        if self.client:
            await self.client.close()
