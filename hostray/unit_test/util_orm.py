# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Tuesday, 12th November 2019 by hsky77 (howardlkung@gmail.com)
'''

import unittest
import asyncio
from enum import Enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Session

from ..util.orm import get_declarative_base, EntityBaseAddon, OrmAccessWorkerPool, OrmDBEntityAccessor, DB_MODULE_NAME, get_session_maker
from .base import UnitTestCase

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
    note = Column(String(100))
    schedule = Column(DateTime, default=datetime.now)

    column_type_validations = {'gender': GenderType}
    column_fix = ['name']
    client_excluded_columns = ['secret']


class TestAccessor(OrmDBEntityAccessor):
    def __init__(self):
        super().__init__(TestEntity)


class OrmTestCase(UnitTestCase):
    def test(self):
        self.test_orm()
        self.test_orm_pool()

    def test_orm(self):
        sess = get_session_maker(
            DB_MODULE_NAME.SQLITE_MEMORY, DeclarativeBase)()
        self.assertIsInstance(sess, Session)

        test_accessor = TestAccessor()
        entity = test_accessor.add(sess, name='someone', age=30,
                                   gender='male', secret='my secret', note='this is note')

        self.assertEqual(entity.name, 'someone')
        self.assertEqual(entity.age, 30)
        self.assertEqual(entity.gender, 'male')
        self.assertEqual(entity.secret, 'my secret')
        self.assertEqual(entity.note, 'this is note')

        test_accessor.save(sess)
        test_accessor.refresh(sess, entity)
        test_accessor.set_attribute(sess, entity, age=50, gender='female')

        self.assertEqual(entity.name, 'someone')
        self.assertEqual(entity.age, 50)
        self.assertEqual(entity.gender, 'female')
        self.assertEqual(entity.secret, 'my secret')
        self.assertEqual(entity.note, 'this is note')

        try:
            test_accessor.set_attribute(sess, entity, name='sometwo')
        except:
            self.assertEqual(entity.name, 'someone')
            test_accessor.rollback(sess)
            test_accessor.refresh(sess, entity)

        self.assertTrue('secret' in entity.to_dict())
        self.assertFalse('secret' in entity.to_client_dict())
        sess.close()

    def test_orm_pool(self):
        db_pool = OrmAccessWorkerPool()
        try:
            self.do_test_pool(db_pool)
        finally:
            db_pool.dispose()

    def do_test_pool(self, db_pool):
        db_pool.set_session_maker(
            DB_MODULE_NAME.SQLITE_MEMORY, DeclarativeBase)

        async def test_db_async():
            await db_pool.reset_connection_async()
            entity = db_pool.run_method(test_accessor.add, name='someone', age=50,
                                        gender='female', secret='my secret', note='this is note')

            self.assertIsNotNone(entity)
            self.assertEqual(entity.name, 'someone')
            self.assertEqual(entity.age, 50)
            self.assertEqual(entity.gender, 'female')
            self.assertEqual(entity.secret, 'my secret')
            self.assertEqual(entity.note, 'this is note')
            db_pool.run_method(test_accessor.save)

            with db_pool.reserve_worker() as identity:
                try:
                    db_pool.run_method(test_accessor.set_attribute,
                                       entity, age=18, identity=identity)
                    self.assertEqual(entity.name, 'someone')
                    self.assertEqual(entity.age, 18)
                    self.assertEqual(entity.gender, 'female')
                    self.assertEqual(entity.secret, 'my secret')
                    self.assertEqual(entity.note, 'this is note')

                    db_pool.run_method(test_accessor.flush, identity=identity)
                    db_pool.run_method(test_accessor.set_attribute,
                                       entity, gender='Gender', identity=identity)  # raise exception
                except:
                    db_pool.run_method(
                        test_accessor.rollback, identity=identity)
                    db_pool.run_method(test_accessor.refresh,
                                       entity, identity=identity)
                    self.assertEqual(entity.name, 'someone')
                    self.assertEqual(entity.age, 50)
                    self.assertEqual(entity.gender, 'female')
                    self.assertEqual(entity.secret, 'my secret')
                    self.assertEqual(entity.note, 'this is note')

            async with db_pool.reserve_worker_async() as identity:
                try:
                    entity = await db_pool.run_method_async(
                        test_accessor.load, identity=identity, name='someone')

                    self.assertIsNotNone(entity)
                    self.assertEqual(entity.name, 'someone')
                    self.assertEqual(entity.age, 50)
                    self.assertEqual(entity.gender, 'female')
                    self.assertEqual(entity.secret, 'my secret')
                    self.assertEqual(entity.note, 'this is note')

                    await db_pool.run_method_async(test_accessor.set_attribute,
                                                   entity, age=18, identity=identity)
                    self.assertEqual(entity.name, 'someone')
                    self.assertEqual(entity.age, 18)
                    self.assertEqual(entity.gender, 'female')
                    self.assertEqual(entity.secret, 'my secret')
                    self.assertEqual(entity.note, 'this is note')
                    db_pool.run_method(test_accessor.flush, identity=identity)
                    await db_pool.run_method_async(test_accessor.set_attribute,
                                                   entity, gender='Gender', identity=identity)  # raise exception
                except:
                    await db_pool.run_method_async(test_accessor.rollback, identity=identity)
                    await db_pool.run_method_async(test_accessor.refresh, entity, identity=identity)
                    self.assertEqual(entity.name, 'someone')
                    self.assertEqual(entity.age, 50)
                    self.assertEqual(entity.gender, 'female')
                    self.assertEqual(entity.secret, 'my secret')
                    self.assertEqual(entity.note, 'this is note')

        test_accessor = TestAccessor()
        entity = db_pool.run_method(test_accessor.add, name='someone', age=50,
                                    gender='male', secret='my secret', note='this is note')

        self.assertIsNotNone(entity)
        self.assertEqual(entity.name, 'someone')
        self.assertEqual(entity.age, 50)
        self.assertEqual(entity.gender, 'male')
        self.assertEqual(entity.secret, 'my secret')
        self.assertEqual(entity.note, 'this is note')

        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_db_async())
