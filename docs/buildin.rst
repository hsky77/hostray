Build-in Modules
*************************

.. contents:: Table of Contents

Controllers
=========================

The controllers are the implementation of `RESTful apis <https://restfulapi.net/>`__ to handle the incomming requests. 

config format:

.. code-block:: yaml
    :linenos:

    controller:
        /api_route:                     # api routing path
            enum: key                   # key of ControllerType
            params:                     # arguments of _initialize()
                ...

Build-in Controllers
----------------------------------------

:enum Frontend = ('frontend', 'tornado.web', 'StaticFileHandler'):

    enable a general web http server, this controller directly import 
    `tornado.web.StaticFileHandler <https://www.tornadoweb.org/en/stable/web.html#tornado.web.StaticFileHandler>`__

    config:

    .. code-block:: yaml
        :linenos:

        controller:
            /(.*):                                  # handle all route
                enum: frontend
                params:
                    path: frontend                  # directory path named frontend under project directory
                    default_filename: index.html    # default page

:enum SystemAlive = ('server_alive', 'default_controller', 'SystemAliveController'):

    handle rest get and response 1 to check server is alive

    config:

    .. code-block:: yaml
        :linenos:

        controller:
            /alive:
                enum: server_alive

:enum ComponentsInfo = ('components_info', 'default_controller', 'ComponentsInfoController'):

    handle rest get and response with the current condition of server loaded components

    config:

    .. code-block:: yaml
        :linenos:

        controller:
            /components_info:
                enum: components_info

Components
=========================

The components of **hostray** act like the functional utilities to help controller development. **hostray** implements 
a simple `composite pattern <https://en.wikipedia.org/wiki/Composite_pattern>`__ to extend the functionalities of project directorys. 
Config format vary.

Build-in Default Components
----------------------------------------

.. Attention:: **default components** are always loaded when api server start.

:enum Localization = ('localization', 'default_component', 'LocalizationComponent'):

    provides language localization, parameter ``dir`` is the path of directory that store the language ``.csv`` files under project directory

    config:

    .. code-block:: yaml
        :linenos:

        component:
            localization:
                dir: 'files'                # load all of the .csv files in files/

    ``.csv`` file example:
    
    .. parsed-literal::

        code,en,tw
        10000,"this is code 10000",這是 code 10000

    code: class reference

    .. code-block:: python
        :linenos:

        from hostray.web.controller import RequestController
        from hostray.web.component import DefaultComponentTypes

        class FooController(RequestController):
            async def get(self):
                comp = self.component_manager.get_component(DefaultComponentTypes.Localization)
                self.write(comp.get_message(10000))

:enum Logger = ('logger', 'default_component', 'LoggerComponent'):

    provides **hostray** customized logger, parameter ``dir`` is the path of directory that store the log outputs under project directory

    .. code-block:: yaml
        :linenos:

        component:
            logger:
                dir: 'logs'

:enum Callback = ('callback', 'default_component', 'CallbackComponent'):

    callback management with ``enums``, no configuration

:enum WorkerPool = ('worker_pool', 'default_component', 'WorkerPoolComponent'):

    provides blocking thread pools to execute functions

    .. code-block:: yaml
        :linenos:

        component:
            worker_pool:
                default: 2      # pool key 'default' with 2 threads maximum

:enum TaskQueue = ('task_queue', 'default_component', 'TaskQueueComponent'):

    provides non-blocking thread pool to execute functions

    .. code-block:: yaml
        :linenos:

        component:
            task_queue:
                worker_count: 2      # 2 threads maximum


Build-in Optional Components 
----------------------------------------

:enum Service = ('services', 'optional_component', 'ServicesComponent'):

    invokes api, specified rest request method name to enable/disable

    .. code-block:: yaml
        :linenos:

        component:
            services:
                some_url:                       # url
                    /:                          # api_route
                        name: test_www          # name of this invoker
                        get:                    # enable method get
                        post:                   # enable method post
                        # put:                  # marked, so disable method put
                        delete:                 # enable method delete

:enum MemoryCache = ('memory_cache', 'optional_component', 'MemoryCacheComponent'):

    simple cache system for backend servers

    .. code-block:: yaml
        :linenos:

        component:
            memory_cache:
                sess_lifetime: 600          # lifetime in seconds
                save_file: file_name        # if specified, save/restore current cache to file when server start/close

:enum OrmDB = ('orm_db', 'optional_component', 'OrmDBComponent'):

    orm component for accessing databases based on `sqlalchemy <https://www.sqlalchemy.org/>`__

    .. code-block:: yaml
        :linenos:

        component:
            orm_db:
                db_0:                               # key of db module
                    module: sqlite_memory           # use sqlite_memory
                    worker: 1                       # number of db access worker (connection)
                    connection_refresh: 60          # minimum interval in seconds to reconnect db

                db_1:
                    module: sqlite                  # use sqlite
                    worker: 1
                    connection_refresh: 60
                    file_name: data.db              # sqlite file path under project directory

                db_2:
                    module: mysql                   # use mysql
                    worker: 1
                    connection_refresh: 60
                    host: xxx.xxx.xxx.xxx           # mysql host ip
                    port: xxxxx                     # mysql host port
                    db_name: xxxxxxx                # mysql database_name
                    user: xxxxxxxx                  # mysql login user
                    password: xxxxxxxx              # mysql login password

    .. Note:: the worker instances keep the sessions and database connections.

Unittest Cases
==========================

**hostray** reserves module **unit_test** base on `unittest <https://docs.python.org/3/library/unittest.html>`__ to test the server project or **hostray** library.
Define enum inherits hostray.unit_test.UnitTestTypes to allow **hostray** tests the project
