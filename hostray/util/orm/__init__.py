# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
This module wraps "SQLAlchemy (https://www.sqlalchemy.org/)" to provide simplified usage in both sync and async execution.

    Usages:

    # Define Database Entity and accessor, accessor defines how the entities are accessed, 
      OrmDBEntityAccessor defines the basic usage to access one type of entity

        from hostray.util.orm import get_declarative_base, EntityBaseAddon, OrmDBEntityAccessor

        DeclarativeBase = get_declarative_base()

        class GenderType(Enum):
            Male = 'male'
            Female = 'female'

        class TestEntity(DeclarativeBase, EntityBaseAddon):
            __tablename__ = 'test'

            id = Column(Integer, primary_key=True)
            name = Column(String(40), nullable=False)
            age = Column(Integer, nullable=False)
            gender = Column(String(6), nullable=False)
            secret = Column(String(40))

            column_type_validations = {'gender': GenderType}        # validate column data is specified types
            column_fix = ['name']                                   # indicate the columns is not allowed to "update"
            client_excluded_columns = ['secret']                    # indicate calling to_client_dict() returns the dict excludes the columns

        class TestAccessor(OrmDBEntityAccessor):
            def __init__(self):
                super().__init__(TestEntity)

    # Usage with OrmAccessWorkerPool and reserve the same worker to execute accessor's functions

        from hostray.util.orm import OrmAccessWorkerPool

        pool = OrmAccessWorkerPool()
        pool.set_session_maker(DB_MODULE_NAME.SQLITE_MEMORY, DeclarativeBase)

        # identity is a hash string to get the same worker (thread) instance for execution
        # the reservation will be released when leaving the "with" clause

        # async usage
        async with db_pool.reserve_worker_async() as identity:
            entity = await pool.run_method_async(accessor.add, name='someone', age=30, gender='male', secret='my secret', identity=identity)
            await pool.run_method_async(accessor.set_attribute, entity, age=50, gender='female', identity=identity)
            await pool.run_method_async(accessor.save, identity=identity)
            await pool.run_method_async(accessor.refresh, entity, identity=identity)

        # sync usage
        with db_pool.reserve_worker() as identity:
            pool.run_method(accessor.set_attribute, entity, age=50, gender='female', identity=identity)
            pool.run_method(accessor.save, identity=identity)
            pool.run_method(accessor.refresh, entity, identity=identity)


Last Updated:  Monday, 4th November 2019 by hsky77 (howardlkung@gmail.com)
'''

from .access_executor_pool import OrmAccessWorkerPool, DB_MODULE_NAME, get_session_maker
from .entity import get_declarative_base, EntityBaseAddon, OrmDBEntityAccessor, DeclarativeMeta
