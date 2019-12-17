Usage of Utils
*********************************

Worker
=================================

``hostray.util.worker`` based on `threading <https://docs.python.org/3/library/threading.html>`__ customized workers (thread classes) and pools to manage the non-async and async executions
and provides context manager functions called ``reserve_worker`` and ``reserve_worker_async`` to exexutes the given functions in the same worker.

Workers are the wrappers of `threading <https://docs.python.org/3/library/threading.html>`__ customized for different operations:

    * ``hostray.util.worker.Worker``: ``run_method`` executes the given function once
    * ``hostray.util.worker.FunctionQueueWorker``: ``run_method`` queues the given functions and execute them when worker is free
    * ``hostray.util.worker.FunctionLoopWorker``: ``run_method`` executes and loop the the given function with the specfied interval

    examples:

    .. code-block:: python

        import time
        from hostray.util import Worker, FunctionLoopWorker, FunctionQueueWorker

        def foo(index, kwindex):
            print(index)

        print('Worker')
        with Worker() as worker:
            worker.run_method(foo, 1, kwindex=2)

            while worker.is_func_running:                   # wait for executions
                pass

        print('FunctionQueueWorker')
        with FunctionQueueWorker() as worker:
            worker.run_method(foo, 1, kwindex=2)
            worker.run_method(foo, 2, kwindex=2)
            worker.run_method(foo, 3, kwindex=2)

            while worker.pending_count > 0:                 # wait for executions
                pass

        print('FunctionLoopWorker')
        with FunctionLoopWorker(loop_interval_seconds=0.1) as worker:
            wait_time = 0.5
            worker.run_method(foo, 1, kwindex=2)

            start_time = time.time()
            while time.time() - start_time < wait_time:     # wait for executions
                pass

        '''
        Output:

        Worker
        1
        FunctionQueueWorker
        1
        2
        3
        FunctionLoopWorker
        1
        1
        1
        1
        1
        '''

Pools manage workers to handle sync and async executions:

    * ``hostray.util.worker.WorkerPool``: worker management and handle sync functions
    * ``hostray.util.worker.AsyncWorkerPool``: add async functions to ``hostray.util.workerWorkerPool``

    example:

    .. code-block:: python
        
        import asyncio
        from hostray.util import AsyncWorkerPool

        ap = AsyncWorkerPool(worker_limit=3)

        def foo(index, kwindex):
            print(index)

        print('run sync')
        with ap.reserve_worker() as identity:
            ap.run_method(foo, 1, 1, identity=None)         # run in free worker
            ap.run_method(foo, 2, 2, identity=identity)     # run in reserved worker

        async def async_foo():
            async with ap.reserve_worker_async() as identity:
                await ap.run_method_async(foo, 1, 1, identity=None)         # run in free worker
                await ap.run_method_async(foo, 2, 2, identity=identity)     # run in reserved worker

        loop = asyncio.get_event_loop()

        print('run async')
        loop.run_until_complete(async_foo())

        ap.dispose()

        '''
        Output:

        run sync
        1
        2
        run async
        1
        2
        '''

        

ORM
=================================

`sqlalchemy <https://www.sqlalchemy.org/>`__ is popular Python SQL toolkit and Object Relational Mapper (ORM). 
**hostray.util.orm** wraps the ORM modules of `sqlalchemy <https://www.sqlalchemy.org/>`__ to simplify usage of database

    * ``hostray.util.orm.DB_MODULE_NAME``: ``enum`` defines the type of database access modules in ``SQLITE_MEMORY``, ``SQLITE_FILE``, and ``MYSQL``.
    * ``hostray.util.orm.get_declarative_base``: function returns key-managed singleton `sqlalchemy.ext.declariative.api.DeclarativeMeta <https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/api.html>`__
    * ``hostray.util.orm.get_session_maker``: function returns `sqlalchemy.orm.Session <https://docs.sqlalchemy.org/en/13/orm/session.html>`__
    * ``hostray.util.orm.EntityBaseAddon``: add helper functions to entity classes
    * ``hostray.util.orm.OrmAccessWorkerPool``: class manages database access workers
    * ``hostray.util.orm.OrmDBEntityAccessor``: class defines how to access database with entity instances

    example:

    .. code-block:: python

        from enum import Enum
        from datetime import datetime

        from sqlalchemy import Column, Integer, String, DateTime
        from sqlalchemy.orm import Session

        from hostray.util.orm import (get_declarative_base, EntityBaseAddon, get_session_maker,
                                      OrmAccessWorkerPool, OrmDBEntityAccessor, DB_MODULE_NAME)

        # 1. create a DeclarativeBase metaclass to collect orm table schema
        DeclarativeBase = get_declarative_base()


        class GenderType(Enum):
            Male = 'male'
            Female = 'female'


        # 2. define entity class inherits DeclarativeBase. 
        #    EntityBaseAddon defines the helper functions for OrmDBEntityAccessor
        class PersonEntity(DeclarativeBase, EntityBaseAddon):
            __tablename__ = 'person'

            id = Column(Integer, primary_key=True)
            name = Column(String(40), nullable=False)
            age = Column(Integer, nullable=False)
            gender = Column(String(6), nullable=False)
            secret = Column(String(40))
            note = Column(String(100))
            schedule = Column(DateTime, default=datetime.now)

            column_type_validations = {'gender': GenderType}        # helper for OrmDBEntityAccessor
            column_fix = ['name']                                   # helper for OrmDBEntityAccessor
            client_excluded_columns = ['secret']                    # helper for OrmDBEntityAccessor


        # 3. define accessor class inherits OrmDBEntityAccessor
        #    accessor define how to access database table
        #    OrmDBEntityAccessor define basic usage to access database single table
        class PersonAccessor(OrmDBEntityAccessor):
            def __init__(self):
                super().__init__(PersonEntity) # use PersonEntity

        if __name__ == '__main__':
            # get sqlalchemy Session instance
            sess = get_session_maker(DB_MODULE_NAME.SQLITE_MEMORY, DeclarativeBase)()

            # access database
            accessor = PersonAccessor()
            entity = accessor.add(sess, name='someone', age=30,
                                       gender='male', secret='my secret', note='this is note')

            accessor.save(sess)
            accessor.refresh(sess, entity)
            accessor.set_attribute(sess, entity, age=50, gender='female')

            try:
                accessor.set_attribute(sess, entity, name='sometwo') # exception column 'name' fixed
                accessor.save(sess)
            except:
                accessor.rollback(sess)
                accessor.refresh(sess, entity)

            print(entity.to_dict())
            sess.close()

        '''
        output:

        {'note': 'this is note', 'gender': 'male', 'age': 30, 'id': 1, 'schedule': '2019-12-16 17:49:28.385881', 'secret': 'my secret', 'name': 'someone'}
        '''

    example using pool:

    .. code-block:: python

        from enum import Enum
        from datetime import datetime

        from sqlalchemy import Column, Integer, String, DateTime
        from sqlalchemy.orm import Session

        from hostray.util.orm import (get_declarative_base, EntityBaseAddon,
                                      OrmAccessWorkerPool, OrmDBEntityAccessor, DB_MODULE_NAME)

        # 1. create a DeclarativeBase metaclass to collect table schema
        DeclarativeBase = get_declarative_base()

        class GenderType(Enum):
            Male = 'male'
            Female = 'female'


        # 2. define entity class inherits DeclarativeBase.
        #    EntityBaseAddon defines the helper functions for OrmDBEntityAccessor
        class PersonEntity(DeclarativeBase, EntityBaseAddon):
            __tablename__ = 'person'

            id = Column(Integer, primary_key=True)
            name = Column(String(40), nullable=False)
            age = Column(Integer, nullable=False)
            gender = Column(String(6), nullable=False)
            secret = Column(String(40))
            note = Column(String(100))
            schedule = Column(DateTime, default=datetime.now)

            column_type_validations = {'gender': GenderType}        # helper for OrmDBEntityAccessor
            column_fix = ['name']                                   # helper for OrmDBEntityAccessor
            client_excluded_columns = ['secret']                    # helper for OrmDBEntityAccessor


        # 3. define accessor class inherits OrmDBEntityAccessor
        #    accessor define how to access database table
        #    OrmDBEntityAccessor define basic usage to access database single table
        class PersonAccessor(OrmDBEntityAccessor):
            def __init__(self):
                super().__init__(PersonEntity)  # use PersonEntity


        if __name__ == '__main__':
            pool = OrmAccessWorkerPool()
            pool.set_session_maker(DB_MODULE_NAME.SQLITE_MEMORY, DeclarativeBase)
            accessor = PersonAccessor()

            with pool.reserve_worker() as identity:
                entity = pool.run_method(accessor.add, name='someone', age=30,
                                         gender='male', secret='my secret', note='this is note', identity=identity)

                pool.run_method(accessor.save, identity=identity)
                pool.run_method(accessor.refresh, entity, identity=identity)
                try:
                    
                    pool.run_method(accessor.set_attribute, entity,
                                    name='sometwo', identity=identity)          # exception column 'name' fixed
                    pool.run_method(accessor.save, identity=identity)
                except:
                    pool.run_method(accessor.rollback, identity=identity)
                    pool.run_method(accessor.refresh, entity, identity=identity)

                print(entity.to_dict())

            pool.dispose()

        '''
        output:

        {'schedule': '2019-12-16 17:44:33.229172', 'secret': 'my secret', 'gender': 'male', 'name': 'someone', 'note': 'this is note', 'age': 30, 'id': 1}
        '''

More Support Utilities
=================================

* **Localization** store and mapping the Localized Messages

    example:

    .. code-block:: python

        from hostray.util import Localization

        local = Localization()
        local.import_csv(['xxx.csv'])           # import language file

        print(local.get_message(1111))          # print the code refered message

* **Logger** is customized `logging <https://docs.python.org/3/library/logging.html>`__ module to specfied the logger's `handlers <https://docs.python.org/3/library/logging.handlers.html>`__

    example:

    .. code-block:: python

        from hostray.util import get_Hostray_logger

        logger = get_Hostray_logger('test', log_to_resource=True)   # log to current working directory
        logger.info('hello')

* **dt** is enum specfied datetime string parser to parse specfied format

    example:

    .. code-block:: python

        from hostray.util import datetime_to_str, str_to_datetime, DATETIME_TYPE

        dt = str_to_datetime('2019-12-17T12:02:58')         # parse dot net format string
        print(dt)                                           # python datetime string
        print(datetime_to_str(dt, DATETIME_TYPE.DTF1))      # to dot net datetime string

        '''
        output
        
        2019-12-17 12:02:58
        2019-12-17T12:02:58.000000
        '''

* **Callback** is a ``enum`` managed async and sync callback function container.

    example:

    .. code-block:: python

        import asyncio
        from enum import Enum

        from hostray.util import Callbacks

        # 1. define enum and functions
        class TestCallbackType(Enum):
            Event_A = 'a'
            Event_A_Async = 'a_async'


        def test_func_1(i, kwindex):
            print('test_func_1', i)


        def test_func_2(i, kwindex):
            print('test_func_2', i)


        async def test_func_async_1(i, kwindex):
            print('test_func_async_1', i)


        async def test_func_async_2(i, kwindex):
            print('test_func_async_2', i)

        cb = Callbacks(TestCallbackType)

        # 2. add callbacks
        cb.add_callback(TestCallbackType.Event_A, test_func_1)
        cb.add_callback(TestCallbackType.Event_A, test_func_2)
        cb.add_callback(TestCallbackType.Event_A_Async,
                        test_func_async_1)
        cb.add_callback(TestCallbackType.Event_A_Async,
                        test_func_async_2)

        # 3. invoke callbacks
        cb.execute_callback(TestCallbackType.Event_A, 1, kwindex=2)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(cb.execute_callback_async(
            TestCallbackType.Event_A_Async, 1, kwindex=2))

        '''
        output:

        test_func_1 1
        test_func_2 1
        test_func_async_2 1
        test_func_async_1 1
        '''