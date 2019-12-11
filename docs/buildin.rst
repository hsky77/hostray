Configuration and Build-in Modules
****************************************

.. contents:: Table of Contents

Server Configuration
=========================

* **name** server name
* **port** port number
* **debug** enable(True)/disable(False) debug mode
* **ssl**: enable `ssl <https://docs.python.org/3/library/ssl.html>`__ module if specified and start project with subcommand ``-s`` which means hosting on `tornado.httpserver.HTTPServer <https://www.tornadoweb.org/en/stable/httpserver.html#http-server>`__
* **component** block of component configurations
* **controller** block of component configurations

config:

.. code-block:: yaml

    # in server_config.yaml

    name: hostray server                # server name
    port: 8888                          # port number
    debug: True                         # enable debug mode
    ssl:
        crt: xxx.crt                    # path of ssl certificate
        key: xxx.key                    # path of private key file

    controller:
        /api_route:                     # api routing path
            enum: controller_key        # key of ControllerType
            params:                     # input arguments of initialize()
                ...
        ...

    component:
        component_key:                  # key of ComponentType
            ...                         # configuration vary
        ...

Controllers
=========================

The controllers are the implementation of `RESTful APIs <https://restfulapi.net/>`__ to handle the incomming requests. 

config format:

.. code-block:: yaml

    controller:
        /api_route:                     # api routing path
            enum: key                   # key of ControllerType
            params:                     # input arguments of initialize()
                ...

Build-in Controllers
----------------------------------------

:enum hostray.web.controller.DefaultControllerType.Frontend:

    enable a general web http server, this controller directly import 
    `tornado.web.StaticFileHandler <https://www.tornadoweb.org/en/stable/web.html#tornado.web.StaticFileHandler>`__

    :value: ``('frontend', 'tornado.web', 'StaticFileHandler')``

    :parameter:
        * **path**: html directory path under project directory
        * **default_filename**: default index file

    rest: **get**

    config:

    .. code-block:: yaml

        controller:
            /(.*):                                  # handle all routes
                enum: frontend
                params:
                    path: frontend                  
                    default_filename: index.html

:enum hostray.web.controller.DefaultControllerType.SystemAlive:

    response 1 to check server is alive

    :value: ``('server_alive', 'default_controller', 'SystemAliveController')``

    rest: **get**

    config:

    .. code-block:: yaml

        controller:
            /alive:
                enum: server_alive

:enum hostray.web.controller.DefaultControllerType.ComponentsInfo:

    response with the current condition of server loaded components

    :value: ``('components_info', 'default_controller', 'ComponentsInfoController')``

    rest: **get**

    config:

    .. code-block:: yaml

        controller:
            /components_info:
                enum: components_info

Components
=========================

The components of **hostray** is the functional utilities. **hostray** implements a simple 
`composite pattern <https://en.wikipedia.org/wiki/Composite_pattern>`__ to extend the functionalities of project. 
**Configuration format vary**.

Build-in Default Components
----------------------------------------

.. Attention:: **default components** are always loaded when server start.

:enum hostray.web.component.DefaultComponentTypes.Localization:

    provides language localization, parameter ``dir`` is the path of directory that store the language ``.csv`` files under project directory.
    `Class Reference <wfg>`__

    :value: ``('localization', 'default_component', 'LocalizationComponent')``

    :parameters:
        * **dir** - optional: load all of the .csv files in local/ under project directory if specified
        * **lang** - optional: setup language, default: en

    config:

    .. code-block:: yaml

        component:
            localization:
                dir: 'local'        
                lang: 'en'          

    :.csv file example:
    
    .. parsed-literal::

        code,en,tw
        10000,"this is code 10000",這是 code 10000

:enum hostray.web.component.DefaultComponentTypes.Logger:

    provides **hostray** customized logger, parameter ``dir`` is the path of directory that store the log outputs under project directory

    :value: ``('logger', 'default_component', 'LoggerComponent')``
    
    :parameters:
        * **dir** - optional. If specified, save log to the folder under porject directory

    config:

    .. code-block:: yaml

        component:
            logger:
                dir: 'logs'

:enum hostray.web.component.DefaultComponentTypes.Callback:

    callback management with customized ``enums``, no configuration

    :value: ``('callback', 'default_component', 'CallbackComponent')``


:enum hostray.web.component.DefaultComponentTypes.WorkerPool:

    provides blocking thread pools to execute functions

    :value: ``('worker_pool', 'default_component', 'WorkerPoolComponent')``

    :parameters:
        **pool_id** : **workers** - specified pool id and the number of workers of that pool

    config:

    .. code-block:: yaml

        component:
            worker_pool:
                default: 2

:enum hostray.web.component.DefaultComponentTypes.TaskQueue:

    provides non-blocking thread pool to execute functions

    :value: ``('task_queue', 'default_component', 'TaskQueueComponent')``

    :parameters:
        * **worker_count** - number of queues

    .. code-block:: yaml

        component:
            task_queue:
                worker_count: 2


Build-in Optional Components 
----------------------------------------

:enum hostray.web.component.OptionalComponentTypes.Service:

    invokes web api, specified method name to enable rest mehtods

    :value: ``('services', 'optional_component', 'ServicesComponent')``

    :parameters:
        * **url** - url
        * **route** - api route
        * **name** - id 
        * **method_names** - rest method names

    config:

    .. code-block:: yaml

        component:
            services:
                https://www.google.com:         # url
                    /:                          # api_route
                        name: google            # name of this invoker
                        get:                    # enable method get

:enum hostray.web.component.OptionalComponentTypes.MemoryCache:

    simple cache(session) system

    :value: ``('memory_cache', 'optional_component', 'MemoryCacheComponent')``

    :parameters:
        * **sess_lifetime** - session lifetime in seconds
        * **renew_lifetime** - renew lifetime when accquire session
        * **renew_id** - renew session id (token) when accquire session
        * **save_file** - save/reload cache file if specified

    config:

    .. code-block:: yaml

        component:
            memory_cache:
                sess_lifetime: 600
                save_file: file_name
                renew_lifetime: False
                renew_id: False

:enum hostray.web.component.OptionalComponentTypes.OrmDB:

    orm component for accessing databases based on `sqlalchemy <https://www.sqlalchemy.org/>`__ which support many backend databses.

    :value: ``('orm_db', 'optional_component', 'OrmDBComponent')``

    :parameters:

        * **db_id** - specified and used in code

            * **module** - switch parameter: 'sqlite_memory', 'sqlite', 'mysql'
            * **connection_refresh** - minimum interval in seconds to refresh connection, no effect in module 'sqlite_memory'
            * **worker** - number of db access worker (connections)
            * **db_connection_parameters** - vary in different modules, check the following config example

    config:

    .. code-block:: yaml

        component:
            orm_db:
                db_0:                               # id of db module
                    module: sqlite_memory           # switch: use sqlite_memory
                    worker: 1                       # number of db access worker (connection)
                    connection_refresh: 60          # no effect

                db_1:
                    module: sqlite                  # switch: use sqlite
                    worker: 1
                    connection_refresh: 60          # minimum interval in seconds to refresh connection
                    file_name: data.db              # sqlite file path under project directory

                db_2:
                    module: mysql                   # switch: use mysql
                    worker: 1
                    connection_refresh: 60          # minimum interval in seconds to refresh connection
                    host: xxx.xxx.xxx.xxx           # mysql host ip
                    port: 3306                      # mysql host port
                    db_name: xxxxxxx                # mysql database_name
                    user: xxxxxxxx                  # mysql login user
                    password: xxxxxxxx              # mysql login password

.. Note:: The worker instances hold the sessions and database connections and refresh them until next db accession consider the parameter 'connection_refresh' as the minimum interval.

.. Note:: Module 'sqlite_memory' does not refresh connections since it is a memory database and will be released if the connection closed.

Unittest Cases
==========================

**hostray** reserves module **unit_test** base on `unittest <https://docs.python.org/3/library/unittest.html>`__ to test the server project or **hostray** library.
Define enum inherits `hostray.unit_test.UnitTestTypes <web_refer.html#hostray.unit_test.UnitTestCase>`__ to allow **hostray** tests projects

* Run test in command prompt:

    * Test hostray library: ``python3 -m hostray test`` 
    * Test hostray project: ``python3 -m hostray test <project directory path>`` 