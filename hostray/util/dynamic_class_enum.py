# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Monday, 4th November 2019 by hsky77 (howardlkung@gmail.com)
'''


from enum import Enum, EnumMeta
from typing import Type, List

from .localization import LocalizedMessageException
from .constants import LocalCode_Must_Be_3Str_Tuple, LocalCode_Must_Be_Class, LocalCode_Must_Be_Function, LocalCode_Is_Not_Subclass


class DynamicClassEnumMeta(EnumMeta):
    """customized enum meta class to import class dynamically"""
    def __new__(metacls, cls, bases, classdict):
        cls = super().__new__(metacls, cls, bases, classdict)
        cls._check_element()
        return cls

    def __call__(cls: Enum, value, names=None, *, module=None, qualname=None, type=None, start=1):
        if names is None:
            return cls._create_instance(value)
        return cls._create_(value, names, module=module, qualname=qualname, type=type, start=start)

    def _create_instance(cls, value):
        for member in cls.__members__.values():
            if member.value[0] == value:
                return member

        return cls.__new__(cls, value)

    def _check_element(cls):
        for e in cls:
            if type(e.value) is not tuple:
                raise LocalizedMessageException(LocalCode_Must_Be_3Str_Tuple)
            else:
                if len(e.value) == 3:
                    for s in e.value:
                        if not isinstance(s, str):
                            raise LocalizedMessageException(
                                LocalCode_Must_Be_3Str_Tuple)
                else:
                    raise LocalizedMessageException(
                        LocalCode_Must_Be_3Str_Tuple)


class DynamicClassEnum(Enum, metaclass=DynamicClassEnumMeta):
    """
    customized enum class to import class dynamically

    every element must be 3 string tuple as (<enum_type_key>, <module>, <class or function>)

    example:
        class TestType(DynamicClassEnum):
            Class1 = ('class1', 'module', 'class')
    """
    pass

    def import_class(self, cls_type: type = None) -> Type:
        from . import get_class
        from inspect import isclass
        try:
            cls = get_class(self._get_module_name(),
                            self.enum_object_type_name)
        except:
            cls = get_class(self.enum_module_name, self.enum_object_type_name)

        if not isclass(cls):
            raise LocalizedMessageException(LocalCode_Must_Be_Class, cls)

        if cls_type is not None and not issubclass(cls, cls_type):
            raise LocalizedMessageException(
                LocalCode_Is_Not_Subclass, cls, cls_type)

        return cls

    def import_function(self) -> Type:
        from . import get_class
        from inspect import isfunction
        try:
            func = get_class(self._get_module_name(),
                             self.enum_object_type_name)
        except:
            func = get_class(self.enum_module_name, self.enum_object_type_name)

        if not isfunction(func):
            raise LocalizedMessageException(LocalCode_Must_Be_Function, func)
        return func

    def _get_module_name(self):
        module_name = self.__module__
        if self.enum_module_name is not None or not self.enum_module_name == '':
            module_name = '{}.{}'.format(module_name, self.enum_module_name)
        return module_name

    @property
    def enum_key(self) -> str:
        return self.value[0]

    @property
    def enum_module_name(self) -> str:
        return self.value[1]

    @property
    def enum_object_type_name(self) -> str:
        return self.value[2]

    @staticmethod
    def get_dynamic_class_enum_class(module_dir: str) -> List[Enum]:
        from importlib import import_module
        from inspect import ismodule
        m = import_module(module_dir)
        return [cls for cls in [getattr(m, k) for k in dir(m) if not k.startswith('__')] if (
            not ismodule(cls) and issubclass(cls, DynamicClassEnum) and not cls is DynamicClassEnum)]
