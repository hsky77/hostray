``hostray.web`` Reference
*****************************

.. contents:: Table of Contents

Controllers
===================

.. class:: hostray.web.controller.ControllerAddon

    A helper class defines quick function access components

    sub_classes:

        * `hostray.web.controller.RequestController <web_refer.html#hostray.web.controller.RequestController>`__
        * `hostray.web.controller.WebSocketController <web_refer.html#hostray.web.controller.WebSocketController>`__

    .. function:: get_localized_message(code\: Union[str, int], \*args) -> str

        quick function to get localized message by 

    .. function:: run_method_async(func\: Callable, \*args, pool_id\: str = 'default', \**kwargs) -> Any

        awaitable, quick function to execute function in pool

    .. function:: log_info(msg\: str, \*args, exc_info=None, extra=None, stack_info=False) -> None

        quick function to log info level message

    .. function:: log_warning(msg\: str, \*args, exc_info=None, extra=None, stack_info=False) -> None

        quick function to log warning level message

    .. function:: log_error(msg\: str, \*args, exc_info=None, extra=None, stack_info=False) -> None

        quick function to log error level message by 

    .. function:: invoke_service_async(service_name \: str, method \: str = 'get', streaming_callback \: Callable = None, \**kwargs) -> Response

        awaitable, quick function to send http request by service Component

.. class:: hostray.web.controller.RequestController

    Class inherits from `tornado.web.RequestHandler <https://www.tornadoweb.org/en/stable/web.html#request-handlers>`__.
    Please check the usage of tornado documentation

.. class:: hostray.web.controller.StreamingDownloadController

    abstract class inherits from `hostray.web.controller.RequestController <web_refer.html#hostray.web.controller.RequestController>`__.

    .. function:: _prepare_binary()-> bytes

        override this awaitable function to prepare binary data for downloading

.. class:: hostray.web.controller.StreamingUploadController

    Abstract class inherits from `hostray.web.controller.RequestController <web_refer.html#hostray.web.controller.RequestController>`__.

    .. function:: _on_chunk_received(self, headers, chunk, bytes_size_received):

        override this function to process incoming chunk data

    .. function:: _on_data_received(self, headers, bytes_size_received):

        override this function to do process after data transaction completed

.. class:: hostray.web.controller.StreamingFileUploadController

    Class inherits from `hostray.web.controller.RequestController <web_refer.html#hostray.web.controller.RequestController>`__.

.. class:: hostray.web.controller.WebSocketController

    Class inherits from `tornado.websocket.WebSocketHandler <https://www.tornadoweb.org/en/stable/websocket.html#tornado.websocket.WebSocketHandler>`__.
    Please check the usage of tornado documentation

Components
===================

.. class:: hostray.web.component.default_component.Component

    base abstract class of component

    .. function:: init(component_manager, \*arugs, \*\*kwargs) -> None

        called when component_manager initialize component objects

    .. function:: info() -> Dict
    
        return define meta information of component

    .. function:: dispose(component_manager) -> None

        called when server stop

.. Note::
    Be aware of the component dependencies when server start/stop, the loaded components are sorted by the order of enums:
    
    server start
        **DefaultComponentTypes** -> **OptionalComponentTypes** -> **Project_ComponentTypes**
    server stop
        **Project_ComponentTypes** -> **OptionalComponentTypes** -> **DefaultComponentTypes**

.. class:: hostray.web.component.default_component.ComponentManager

    contain and manage the loaded components

    .. function:: @property components -> List[Component]

        return list of loaded components

    .. function:: @property info -> Dict

        return info of loaded components

    .. function:: dispose() -> None

        call dispose() of loaded components

    .. function:: boardcast(method\: str, \*arugs, \*\*kwargs) -> List[Tuple[ComponentTypes, Any]]

        invokes the non-awaitable method of stored components and
        return a list of returns from each component method

        * **method**: str, method name 
        * **\*args**: variable number of arguments of method
        * **\**kwargs**: keyworded, variable-length argument list of method

    .. function:: boardcast_async(method\: str, \*arugs, \*\*kwargs) -> List[Tuple[ComponentTypes, Any]]

        invokes both awaitable and non-awaitable method of stored components and 
        return a list of returns from each component method

        * **method**: str, method name 
        * **\*args**: variable number of arguments of method
        * **\**kwargs**: keyworded, variable-length argument list of method  

    .. function:: invoke(enum_type\: ComponentTypes, method\: str, \*arugs, \**kwargs) -> Any

        execute component mehtod by giving the method name and arguments

        * **enum_type**: ComponentTypes enum type
        * **method**: str, method name 
        * **\*args**: variable number of arguments of method
        * **\**kwargs**: keyworded, variable-length argument list of method          

    .. function:: invoke_async(enum_type\: ComponentTypes, method\: str, \*arugs, \**kwargs) -> Any

        asynchronously execute component mehtod by giving the method name and arguments

        * **enum_type**: ComponentTypes enum type
        * **method**: str, method name 
        * **\*args**: variable number of arguments of method
        * **\**kwargs**: keyworded, variable-length argument list of method   

    .. function:: set_component(component\: Component) -> None

        add or replace component instance

        * **component**: Component instance

    .. function:: get_component(enum_type\: ComponentTypes) -> Union[Component, None]

        return stored component instance or None

        * **enum_type**: ComponentTypes enum type

    .. function:: pick_component(enum_types\: List[ComponentTypes]) -> Union[Component, None]

        return the first founded stored component object of enum_types

        * **enum_type**: ComponentTypes enum type

    .. function:: has_component(enum_type\: ComponentTypes) -> bool

        check whether component exists

        * **enum_type**: ComponentTypes enum type

    .. function:: sort_components(order_list\: List[ComponentTypes]) -> None

        sort component object with ComponentTypes in order

        * **order_list**: list of ComponentTypes

.. class:: hostray.web.component.default_component.LocalizationComponent

    .. function:: set_language(lang\: str) -> None

        set language

        * **lang**: key of language such as 'en'

    .. function:: get_message(code\: str, \*args) -> str

        return the message refer to 'code' and \*args

        * **code**: localized message code
        * **\*args**: variable number of arguments of ``str``

    sample:

    .. code-block:: python

        from hostray.web.controller import RequestController
        from hostray.web.component import DefaultComponentTypes

        class FooController(RequestController):
            async def get(self):
                comp = self.component_manager.get_component(DefaultComponentTypes.Localization)
                self.write(comp.get_message(10000))
                
.. class:: hostray.web.component.default_component.LoggerComponent

    .. function:: set_default_logger_echo(echo\: bool) -> None

        enable/disable default loggers print to stdout

        * **echo**: print log to command prompt

    .. code-block:: python

        default_loggers = ['tornado.access',
                           'tornado.application',
                           'tornado.general',
                           'sqlalchemy']

    .. function:: get_logger(name\: str, sub_dir\: str = '', mode\: str = 'a', encoding\: str = 'utf-8', echo\: bool = False) -> HostrayLogger

        get HostrayLogger singleton object

        * **name**: logger name
        * **sub_dir**: specfied sub dir of log dir if enable logging to file
        * **mode**: filemode
        * **encoding**: text encoding
        * **echo**: print log to command prompt

    sample:

    .. code-block:: python
    
        from hostray.web.controller import RequestController
        from hostray.web.component import DefaultComponentTypes

        class FooController(RequestController):
            async def get(self):
                comp = self.component_manager.get_component(DefaultComponentTypes.Logger)
                logger = comp.get_logger('some_logger')

.. class:: hostray.web.component.default_component.CallbackComponent

    .. function:: get_callback_obj(enum_cls\: Enum) -> Callbacks

        return callback function instance

        * **enum_cls**: class of ``enum``

    .. function:: add_callback(callback_enum_type\: Enum, callback\: Callable) -> None

        registered callback function instance

        * **callback_enum_type**: type class of ``enum``
        * **callback**: callback function

    .. function:: remove_callback(callback_enum_type\: Enum, callback\: Callable) -> None

        remove callback function instance

        * **callback_enum_type**: type class of ``enum``
        * **callback**: callback function

    .. function:: execute_callback(callback_enum_type\: Enum, \*args, \**kwargs) -> None

        execute registered callback functions

        * **callback_enum_type**: type class of ``enum``
        * **\*args**: variable number of arguments of callback functions
        * **\**kwargs**: keyworded, variable-length argument list of callback functions     

    .. function:: execute_callback_async(callback_enum_type\: Enum, \*args, \**kwargs) -> None

        asynchronously execute registered callback functions

        * **callback_enum_type**: type class of ``enum``
        * **\*args**: variable number of arguments of callback functions
        * **\**kwargs**: keyworded, variable-length argument list of callback functions    

.. class:: hostray.web.component.default_component.TaskQueueComponent

    .. function:: run_method_in_queue(func\: Callable, \*args, on_finish\: Callable[[Any], None] = None, on_exception\: Callable[[Exception], None] = None, \**kwargs) -> None

        queue function and execute in differet thread

        * **func**: function object
        * **\*args**: variable number of arguments of function object
        * **on_finish**: callback when function finished
        * **on_exception**: callback when function exception occurs
        * **\**kwargs**: keyworded, variable-length argument list of function object  

.. Attention:: **run_method_in_queue() Does Not** block the thread

.. class:: hostray.web.component.default_component.WorkerPoolComponent

    .. function:: set_pool(pool_id\: str = 'default', worker_limit\: int = 3) -> None

        creates pool if it does not exist and setup the worker maximum by 'pool_id'

        * **pool_id**: the id of pool
        * **worker_limit**: maximum of workers

    .. function:: run_method(func\: Callable, \*args, pool_id\: str = 'default', \**kwargs) -> Any

        execute func in pool with specfied 'pool_id'

        * **func**: function object
        * **\*args**: variable number of arguments of function object
        * **\**kwargs**: keyworded, variable-length argument list of function object

    .. function:: run_method_async(func\: Callable, \*args, pool_id\: str = 'default', \**kwargs) -> Any

        asynchronously execute func in pool with specfied 'pool_id'

        * **func**: function object
        * **\*args**: variable number of arguments of function object
        * **\**kwargs**: keyworded, variable-length argument list of function object

.. Attention:: **run_method() Does** block the thread

.. class:: hostray.web.component.optional_component.MemoryCacheComponent

    .. function:: get_expired_datetime(session_id: str) -> datetime

        Return the datetime the session id expired

        * **session_id**: session id

    .. function:: get(session_id: str = '', renew_lifetime: bool = False, renew_id: bool = False) -> Tuple[dict, str]

        Return tuple (cache, session_id).

        * **session_id**: session id
        * **renew_lifetime**: renew the expired datetime of the session_id
        * **renew_id**: return new session_id if set to True

    .. function:: save_to_file() -> None

        save current cache to file if the config parameter 'save_file' specfied

    .. function:: load_from_file() -> None

        load file if the config parameter 'save_file' specfied to cache

    .. function:: clear_session(session_id: str) -> None

        clear cache of the session_id

        * **session_id**: session id

.. class:: hostray.web.component.optional_component.OrmDBComponent

    manage `sqlalchemy <https://www.sqlalchemy.org/>`__ db access worker pools and execute ``hostray.util.orm.OrmDBEntityAccessor``

    .. function:: get_pool_obj(db_id: str) -> OrmAccessWorkerPool

        return the db access wokrer pool object of db_id

        * **db_id**: id of db access wokrer pool

    .. function:: get_db_settings(db_id: str) -> Dict

        return the db setting of db_id

        * **db_id**: id of db access wokrer pool

    .. function:: init_db_declarative_base(db_id: str, declared_entity_base: DeclarativeMeta) -> None

        create and initialize `sqlalchemy <https://www.sqlalchemy.org/>`__ orm meta class and engine of db_id

        * **db_id**: id of db access wokrer pool
        * **declared_entity_base**: `sqlalchemy <https://www.sqlalchemy.org/>`__ orm meta class

    .. function:: reserve_worker(db_id: str) -> str

        contextmanager wrapped funciton to reserve worker, return the identity ``str``

        * **db_id**: id of db access wokrer pool

    .. function:: reserve_worker_async(db_id: str) -> str

        asynccontextmanager wrapped funciton to reserve worker, return the identity ``str``

        * **db_id**: id of db access wokrer pool

    .. function:: reset_session(db_id: str, force_reconnect: bool = False) -> None

        reset db session and connection

        * **db_id**: id of db access wokrer pool
        * **force_reconnect**: ignore minimum interval 'connection_refresh' and reset db session and connection

    .. function:: reset_session_async(db_id: str, force_reconnect: bool = False) -> None

        asynchronously reset db session and connection

        * **db_id**: id of db access wokrer pool
        * **force_reconnect**: ignore minimum interval 'connection_refresh' and reset db session and connection

    .. function:: run_accessor(db_id: str, accessor_func: Callable, *args, identity: str = None, **kwargs) -> Any

        execute function of ``hostray.util.orm.OrmDBEntityAccessor``

        * **db_id**: id of db access wokrer pool
        * **accessor_func**: function of ``hostray.util.orm.OrmDBEntityAccessor``
        * **\*args**: variable number of arguments of accessor function object
        * **\**kwargs**: keyworded, variable-length argument list of accessor function object

    .. function:: run_accessor_async(db_id: str, accessor_func: Callable, *args, identity: str = None, **kwargs) -> Any

        asynchronously execute function of ``hostray.util.orm.OrmDBEntityAccessor``

        * **db_id**: id of db access wokrer pool
        * **accessor_func**: function of ``hostray.util.orm.OrmDBEntityAccessor``
        * **\*args**: variable number of arguments of accessor function object
        * **\**kwargs**: keyworded, variable-length argument list of accessor function object

.. class:: hostray.web.component.optional_component.ServicesComponent

    .. function:: invoke(service_name: str, method='get', streaming_callback: Callable = None, **kwargs) -> requests.Response

        seed http request to config specfied service_name and return ``requests.Response`` object

        * **service_name**: config specfied service_name
        * **method**: http methods ``['get', 'post', 'patch', 'put', 'delete', 'option']``
        * **streaming_callback**: streaming operation callback function, check `Reference <https://requests.readthedocs.io/en/master/user/advanced/#streaming-uploads>`__
        * **\**kwargs**: keyworded, variable-length argument list of http method parameters

    .. function:: invoke_async(service_name: str, method='get', streaming_callback: Callable = None, **kwargs) -> requests.Response

        asynchronously seed http request to config specfied service_name and return ``requests.Response`` object

        * **service_name**: config specfied service_name
        * **method**: http methods ``['get', 'post', 'patch', 'put', 'delete', 'option']``
        * **streaming_callback**: streaming operation callback function, check `Reference <https://requests.readthedocs.io/en/master/user/advanced/#streaming-uploads>`__
        * **\**kwargs**: keyworded, variable-length argument list of http method parameters

Unit_test
===============================

.. class:: hostray.unit_test.UnitTestCase

    Abstract class of test case

    .. function:: test() -> None

        override this function to implement unittest code

Configuration Validator 
===============================

.. class:: hostray.web.config_validator.ConfigBaseElementMeta

    base config element metaclass

    .. function:: set_cls_parameters(*cls_parameters) -> None

        **@classmethod**, set the sub class elements

        * **\*parameters**: variable number of arguments of ConfigBaseElementMeta
    
    .. function:: get_cls_parameter(key_routes, delimeter=".") -> type

        **@classmethod**, get the sub class elements

        * **key_routes**: route in ``str``
        * **delimeter**: delimeter of route.split()

    .. function:: get_parameter(key_routes: str, delimeter: str = '.')

        return parameter of specfied key_routes

        * **key_routes**: route in ``str``
        * **delimeter**: delimeter of route.split()

.. class:: hostray.web.config_validator.ConfigContainerMeta

    config validation element metaclass contain sub elements

    .. function:: __new__(name: str, required: bool, *parameters) -> type

        * **name**: name of type
        * **required**: specfied is this element is required in config
        * **\*parameters**: variable number of arguments of ConfigBaseElementMeta

    .. function:: copy(name) -> type

        * **name**: name of copied type

.. class:: hostray.web.config_validator.ConfigElementMeta

    config validation element metaclass store parameters

    .. function:: __new__(name: str, parameter_type: Any, required: bool) -> type

        * **name**: name of type
        * **parameter_type**: variable type such ``str, int, float``
        * **required**: specfied is this element is required in config

    .. function:: copy(name) -> type

        * **name**: name of copied type

.. class:: hostray.web.config_validator.ConfigScalableContainerMeta

    scalable config validation element metaclass contain sub elements metaclass

    .. function:: __new__(parameter_type: Union[str, int], *parameters) -> type

        * **parameter_type**: variable type such ``str, int, float``
        * **\*parameters**: variable number of arguments of ConfigBaseElementMeta

    .. function:: copy(name) -> type

        * **name**: name of copied type

.. class:: hostray.web.config_validator.ConfigScalableElementMeta

    scalable config validation element metaclass

    .. function:: __new__(element_type: Union[str, int], parameter_type: Any) -> type

        * **element_type**: scalable key variable type such as ``str, int, float``
        * **parameter_type**: variable type such as ``str, int, float``

    .. function:: copy(name) -> type

        * **name**: name of copied type

.. class:: hostray.web.config_validator.ConfigSwitchableElementMeta

    switchable config validation element metaclass

    .. function:: __new__(name: str, parameter_type: Any, required: bool, *parameters) -> type

        * **name**: name of type
        * **parameter_type**: variable type
        * **required**: specfied is this element is required in config
        * **\*parameters**: variable number of arguments of ConfigBaseElementMeta

    .. function:: copy(name) -> type

        * **name**: name of copied type

.. class:: hostray.web.config_validator.HostrayWebConfigValidator

    default validator to validate ``server_config.yaml``.

.. class:: hostray.web.config_validator.HostrayWebConfigControllerValidator

    default validator to validate the controller block of ``server_config.yaml``.

.. class:: hostray.web.config_validator.HostrayWebConfigComponentValidator

    default validator to validate the component block of ``server_config.yaml``.

