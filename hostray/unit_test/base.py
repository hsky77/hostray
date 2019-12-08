# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Saturday, 16th November 2019 by hsky77 (howardlkung@gmail.com)
'''

from unittest import TestCase
from typing import List

from ..util import DynamicClassEnum


class UnitTestTypes(DynamicClassEnum):
    """base abstract unitest enum class"""

    @staticmethod
    def get_unittest_enum_class() -> List[DynamicClassEnum]:
        from ..web import Unittest_Module_Folder
        try:
            return DynamicClassEnum.get_dynamic_class_enum_class(Unittest_Module_Folder)
        except:
            pass

    def import_class(self):
        return super().import_class(cls_type=UnitTestCase)


class UnitTestCase(TestCase):
    """hostray unittest case abstract class"""

    def test(self):
        raise NotImplementedError()
