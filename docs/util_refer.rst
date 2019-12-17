``hostray.util`` Reference
*****************************

.. contents:: Table of Contents

Worker
===================

.. class:: hostray.util.worker.Worker

    property:

        * ``is_func_running -> bool``: check if worker is running a function

    .. function:: run_method(func: Callable, *args, on_finish: Callable[[Any], None] = None, on_exception: Callable[[Exception], None] = None, **kwargs) -> bool

        return True if the given function instance is going to be executed

        * **func**: function instance to be executed
        * **on_finish**: callback with the argument of function return after function runned
        * **\*args**: variable number of arguments of method
        * **on_exception**: callback with the argument of Exception after function Exception occured
        * **\**kwargs**: keyworded, variable-length argument list of method

    .. function:: run_method_and_wait(func: Callable, *args, **kwargs) -> Any

        execute function and return the function return (thread-blocking)

        * **func**: function instance to be executed
        * **\*args**: variable number of arguments of method
        * **\**kwargs**: keyworded, variable-length argument list of method

    .. function:: run_method_and_wait_async(func: Callable, *args, **kwargs) -> Awaitable

        asynchronously execute function and return the function return

        * **func**: function instance to be executed
        * **\*args**: variable number of arguments of method
        * **\**kwargs**: keyworded, variable-length argument list of method

.. class:: hostray.util.worker.FunctionQueueWorker

    property:

        * ``pending_count -> int``: return the len of queue

    .. function:: run_method(func: Callable, *args, on_finish: Callable[[Any], None] = None, on_exception: Callable[[Exception], None] = None, **kwargs) -> None

        queue the function instance to be executed when worker is free

        * **func**: function instance to be executed
        * **on_finish**: callback with the argument of function return after function runned
        * **\*args**: variable number of arguments of method
        * **on_exception**: callback with the argument of Exception after function Exception occured
        * **\**kwargs**: keyworded, variable-length argument list of method

.. class:: hostray.util.worker.FunctionLoopWorker

    .. function:: run_method(func: Callable, *args, on_finish: Callable[[Any], None] = None, on_exception: Callable[[Exception], None] = None, **kwargs) -> None

        start and loop the given function instance

        * **func**: function instance to be executed
        * **on_finish**: callback with the argument of function return after function runned for each time
        * **\*args**: variable number of arguments of method
        * **on_exception**: callback with the argument of Exception after function Exception occured for each time
        * **\**kwargs**: keyworded, variable-length argument list of method

    .. function:: stop()
        
        stop if worker is looping function

.. class:: hostray.util.worker.WorkerPool

    property:

        * ``workers() -> List[FunctionQueueWorker]``

    .. function:: dispose() -> None

    .. function:: info() -> Dict

    .. function:: reserve_worker() -> str 

        `@contextmanager <https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager>`__, yield string of identity to reserved worker instance

    .. function:: run_method(func: Callable, *args, identity: str = None, **kwargs) -> Any

        * **func**: function instance to be executed
        * **\*args**: variable number of arguments of method
        * **identity**: identity string from ``reserve_worker``
        * **\**kwargs**: keyworded, variable-length argument list of method

    .. function:: broadcast_method(func_name: str, *args, **kwargs) -> List[Any]

        invoke each worker's function named func_name if it has.

        * **func_name**: function name to be invoked
        * **\*args**: variable number of arguments of method
        * **\**kwargs**: keyworded, variable-length argument list of method

.. class:: hostray.util.worker.AsyncWorkerPool

    inherit from hostray.util.worker.WorkerPool and add asynchronous functions

    .. function:: reserve_worker_async() -> str

        `@asynccontextmanager <https://docs.python.org/3/library/contextlib.html#contextlib.asynccontextmanager>`__, yield string of identity to reserved worker instance,
        **hostray** implements a unofficial one since Python 3.6 does not have it.

    .. function:: run_method_async(func: Callable, *args, identity: str = None, **kwargs) -> Any

        * **func**: function instance to be executed
        * **\*args**: variable number of arguments of method
        * **identity**: identity string from ``reserve_worker``
        * **\**kwargs**: keyworded, variable-length argument list of method

    .. function:: broadcast_method_async(func_name: str, *args, **kwargs) -> List[Any]

        asynchronously invoke each worker's **Awaitable** function named func_name if it has.

        * **func_name**: function name to be invoked
        * **\*args**: variable number of arguments of method
        * **\**kwargs**: keyworded, variable-length argument list of method

Orm
===================

.. function:: get_declarative_base(key: str = 'default') -> DeclarativeMeta

    return key managed ``DeclarativeMeta`` metaclass

    * **key**: key to managed ``DeclarativeMeta`` metaclass

.. function:: get_session_maker(db_module: DB_MODULE_NAME, declared_entity_base: DeclarativeMeta, autoflush: bool = False, **kwargs) -> Session

    return sqlalchemy.orm.Session class type

    * **db_module**: enum ``hostray.util.orm.DB_MODULE_NAME``
    * **declared_entity_base**: all orm entity class should inherits from ``sqlalchemy.ext.declarative.api.DeclarativeMeta`` before call this function
    * **autoflush**: enable/disable ``sqlalchemy.orm.Session autoflush``

.. class:: hostray.util.orm.EntityBaseAddon

    define entity helper functions

    property:

        * ``column_type_validations: Dict[str, Any] = {}``

            indicate the column type for validation

        * ``column_fix: List[str] = []``

            indicate the columns are not allowed to update value

        * ``client_excluded_columns: List[str] = []``

            indicate the excluded columns for the entity data should be response to client

        * ``dt_converter = PY_DT_Converter``

            indicate datetime converter from database to json serializable dict

        * ``identity -> Tuple[Any]``

            return ``tuple`` of columns as identification

        * ``primary_key_args -> Dict[str, Any]``

            return key-value dict of primary key columns

        * ``non_primary_key_args -> Dict[str, Any]``
        
            return key-value dict of non primary key columns

    .. function:: primary_keys() -> List[str]

        return list of primary key column names

    .. function:: non_primary_keys() -> List[str]

        return list of non primary key column names

    .. function:: columns() -> List[str]

        return list of column names

    .. function:: get_primary_key_args(**kwargs) -> Dict[str, Any]

        return key-value dict of primary key columns exist in ``**kwargs``

        * **\**kwargs**: keyworded, variable-length argument list of method

    .. function:: get_non_primary_key_args(**kwargs) -> Dict[str, Any]

        return key-value dict of non primary key columns exist in ``**kwargs``

        * **\**kwargs**: keyworded, variable-length argument list of method

    .. function:: get_entity_args(**kwargs) -> Dict[str, Any]

        return key-value dict of entity variables exist in ``**kwargs``

        * **\**kwargs**: keyworded, variable-length argument list of method

    .. function:: get_non_entity_args(**kwargs) -> Dict[str, Any]

        return key-value dict of non entity variables exist in ``**kwargs``

        * **\**kwargs**: keyworded, variable-length argument list of method

    .. function:: parameter_validation(check_fix: bool = True, **kwargs) -> None

        validate variables in ``**kwargs`` by specfied ``column_type_validations``

        * **check_fix**: raise Exception if check_fix is True

        * **\**kwargs**: keyworded, variable-length argument list of method

    .. function:: to_client_dict() -> Dict[str, Any]

        return dict excludes the keys specfied in ``client_excluded_columns``

    .. function:: to_dict() -> Dict[str, Any]

        return dict of entity columns

    .. function:: equals(r: Entity) -> bool

        return True if r equals this entity

.. class:: hostray.util.orm.OrmDBEntityAccessor

    db access worker owns db session and connection instance based on `sqlalchemy <https://www.sqlalchemy.org/>`__.

    .. function:: set_orm_engine(db_module: DB_MODULE_NAME, declared_entity_base: DeclarativeMeta, autoflush: bool = False, **kwargs) -> None

        setup parameters to create `sqlalchemy.engine.Engine <https://docs.sqlalchemy.org/en/13/core/connections.html#sqlalchemy.engine.Engine>`__ instance

        * **db_module**: enum ``hostray.util.orm.DB_MODULE_NAME``

        * **declared_entity_base**: DeclarativeMeta contains the schema meta of entity class

        * **autoflush**: set autoflash refer to `sqlalchemy.orm.session.sessionmaker <https://docs.sqlalchemy.org/en/13/orm/session_api.html#sqlalchemy.orm.session.sessionmaker>`__

    .. function:: close_session() -> None:

        release the session and connection. 
        
.. attention:: close_session() should also be called in worker thread

.. class:: hostray.util.orm.OrmAccessWorkerPool

    pool of hostray.util.orm.OrmDBEntityAccessor. inherit from `hostray.util.worker.AsyncWorkerPool <util_refer.html#hostray.util.worker.AsyncWorkerPool>`__

    .. function:: enable_orm_log(echo: bool = False) -> None

        enable/disable `sqlalchemy <https://www.sqlalchemy.org/>`__ default logger stdout output

    .. function:: set_session_maker(db_module: DB_MODULE_NAME, declared_entity_base: DeclarativeMeta, autoflush: bool = False, **kwargs) -> None

        setup parameters to create `sqlalchemy.engine.Engine <https://docs.sqlalchemy.org/en/13/core/connections.html#sqlalchemy.engine.Engine>`__ instance

        * **db_module**: enum ``hostray.util.orm.DB_MODULE_NAME``

        * **declared_entity_base**: DeclarativeMeta contains the schema meta of entity class

        * **autoflush**: set autoflash refer to `sqlalchemy.orm.session.sessionmaker <https://docs.sqlalchemy.org/en/13/orm/session_api.html#sqlalchemy.orm.session.sessionmaker>`__

    .. function:: reset_connection() -> None

        release all of the workers' session and connection. 

    .. function:: reset_connection_async() -> None

        asynchronously release all of the workers' session and connection. 

Util
===================

.. function:: get_class(module: str, *attrs) -> type

    return type or function instance of imported module

    example:

    .. code-block:: python

        cls = get_class("module", "class / static function", "class static function")


.. function:: join_to_abs_path(*paths) -> str

    return os.path.join() absolute path in linux format which means replace '\\\\' to '/'


.. function:: join_path(*paths) -> str

    return os.path.join() path in linux format which means replace '\\\\' to '/'

.. function:: walk_to_file_paths(file_or_directory: str) -> List[str]

    return a list of absolutely path from the input directory path recursively or file

.. function:: size_bytes_to_string(f_size: int, units: List[str] = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB']) -> str

    return byte size string in unit

.. function:: generate_base64_uid(byte_length: int = 32, urlsafe: bool = True) -> str

    return customized uuid string

.. function:: convert_tuple_to_dict(t: tuple, key_name: str) -> Dict

    return customized dict from tuple

    example:

    .. code-block:: python

        d = convert_tuple_to_dict((1, 2, 3), 'n'))

        # d is {'n_1': 1, 'n_2': 2, 'n_3': 3}

.. function:: get_host_ip(remote_host: str = '8.8.8.8', port: int = 80) -> str

    return the host ip, no guarantee to get actual host ip