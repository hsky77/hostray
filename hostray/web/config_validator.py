# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Thursday, 7th November 2019 by hsky77 (howardlkung@gmail.com)
'''

from typing import Dict, List, Type, Any, Tuple, Union, Iterable

from enum import Enum

from ..util import HierarchyElementMeta, LocalCode_No_Parameters, LocalCode_Parameters_No_Key
from .constants import Component_Module_Folder, Controller_Module_Folder
from . import (HostrayWebException, LocalCode_Parameter_Required,
               LocalCode_Parameter_Type_Error, LocalCode_Setup_Error,
               LocalCode_Invalid_Parameter)


class ConfigElementType(Enum):
    Container = 'container'
    Element = 'element'
    ScalableContainer = 'scalable_container'
    ScalableElement = 'scalable_element'
    SwitchableElement = 'switchable_element'


class ConfigBaseElementMeta(HierarchyElementMeta):
    def __new__(cls, name: str, parameter_type: Any, required: bool = True, *cls_parameters) -> type:
        return super().__new__(cls, name, (object,), {
            'parameter_type': parameter_type, 'required': required, 'get_parameter': cls.get_parameter})

    def __init__(cls, name: str, parameter_type: Any, required: bool, *cls_parameters) -> None:
        super().__init__(name, (object,), {})
        cls.set_cls_parameters(*cls_parameters)

    def __call__(cls, config: Union[Dict, List, str, int, float, bool], logs: List[str] = None, route: str = ''):
        obj = super().__call__()
        try:
            if config is not None:
                obj.parameter_type(config)
            obj.parameter = config
            obj.config_route = route
            obj._cls = cls
            if isinstance(logs, list) and not isinstance(config, dict):
                logs.append('{}: {}'.format(route, config))
        except:
            raise HostrayWebException(
                LocalCode_Parameter_Type_Error, route, cls.__name__, config, obj.parameter_type.__name__)

        if hasattr(cls, '_cls_parameters'):
            if config is not None:
                ConfigBaseElementMeta._convert_scalable_elements(cls, config)

            for k, v in cls._cls_parameters.items():
                if v.required:
                    if config is None or not k in config:
                        raise HostrayWebException(
                            LocalCode_Parameter_Required, cls.__name__, k)

                if config is not None and k in config:
                    if not hasattr(obj, '_parameters'):
                        obj._parameters = {}
                    obj._parameters[k] = v(config[k], logs, '{}.{}'.format(
                        route, k) if not route == '' else k)
        return obj

    def get_parameter(self, key_routes: str, delimeter: str = '.'):
        routes = key_routes.split(delimeter)
        temp = self
        for key in routes:
            if hasattr(temp, '_parameters'):
                if key in temp._parameters:
                    temp = temp._parameters[key]
                else:
                    raise HostrayWebException(
                        LocalCode_Parameters_No_Key, temp, key)
            else:
                raise HostrayWebException(
                    LocalCode_No_Parameters, temp)

        return temp.parameter

    def _convert_scalable_elements(cls, config: Dict):
        pops = []
        extends = []

        for k in cls._cls_parameters:  # convert scalable elements to identified elements
            if cls._cls_parameters[k].element_type is ConfigElementType.ScalableElement:
                names = [n for n in config if not n in cls._cls_parameters]
                for name in names:
                    extends.append(ConfigElementMeta(
                        name, cls._cls_parameters[k].parameter_type, cls._cls_parameters[k].required))
                pops.append(k)
            elif cls._cls_parameters[k].element_type is ConfigElementType.ScalableContainer:
                names = [cls._cls_parameters[k].parameter_type(
                    n) for n in config if not n in cls._cls_parameters]
                for name in names:
                    extends.append(ConfigContainerMeta(name, cls._cls_parameters[k].required,
                                                       *cls._cls_parameters[k]._cls_parameters.values()))
                pops.append(k)
            elif cls._cls_parameters[k].element_type is ConfigElementType.SwitchableElement:
                if config[k] in cls._cls_parameters[k]._cls_parameters:
                    for _, param_cls in cls._cls_parameters[k]._cls_parameters[config[k]]._cls_parameters.items():
                        extends.append(param_cls)
                    extends.append(
                        ConfigElementMeta(k, cls._cls_parameters[k].parameter_type, cls._cls_parameters[k].required))

                    pops.append(k)
                else:
                    raise HostrayWebException(LocalCode_Setup_Error, cls)

        for k in pops:  # remove scalable or switchable element
            cls._cls_parameters.pop(k)

        for extend in extends:  # add scaled elements
            cls._cls_parameters[extend.__name__] = extend


class ConfigContainerMeta(ConfigBaseElementMeta):
    def __new__(cls, name: str, required: bool, *parameters) -> type:
        return super().__new__(cls, name, dict, required, *parameters)

    def __init__(cls, name: str, required: bool, *parameters) -> None:
        cls.element_type = ConfigElementType.Container
        super().__init__(name, dict, required, *parameters)

    def copy(cls, name):
        if name == cls.__name__:
            raise HostrayWebException(109, name)
        new_cls = ConfigContainerMeta(
            name, cls.required, *cls._cls_parameters.values())
        return new_cls


class ConfigElementMeta(ConfigBaseElementMeta):
    def __new__(cls, name: str, parameter_type: Any, required: bool) -> type:
        return super().__new__(cls, name, parameter_type, required)

    def __init__(cls, name: str, parameter_type: Any, required: bool) -> None:
        cls.element_type = ConfigElementType.Element
        super().__init__(name, parameter_type, required)

    def copy(cls, name):
        if name == cls.__name__:
            raise HostrayWebException(109, name)
        new_cls = ConfigElementMeta(name, cls.parameter_type, cls.required)
        return new_cls


class ConfigScalableContainerMeta(ConfigBaseElementMeta):
    def __new__(cls, parameter_type: Union[str, int], *parameters) -> type:
        return super().__new__(cls, 'ConfigScalableContainerMeta', parameter_type, False, *parameters)

    def __init__(cls, parameter_type: Union[str, int], *parameters) -> None:
        cls.element_type = ConfigElementType.ScalableContainer
        super().__init__('ConfigScalableContainerMeta', parameter_type, False, *parameters)

    def copy(cls):
        new_cls = ConfigScalableContainerMeta(
            cls.parameter_type, *cls._cls_parameters.values())
        return new_cls


class ConfigScalableElementMeta(ConfigBaseElementMeta):
    def __new__(cls, element_type: Union[str, int], parameter_type: Any) -> type:
        return super().__new__(cls, 'ConfigScalableElementMeta', element_type, False)

    def __init__(cls, element_type: Union[str, int], parameter_type: Any) -> None:
        cls.element_type = ConfigElementType.ScalableElement
        super().__init__('ConfigScalableElementMeta', parameter_type, False)

    def copy(cls):
        new_cls = ConfigScalableElementMeta(
            cls.element_type, cls.parameter_type)
        return new_cls


class ConfigSwitchableElementMeta(ConfigBaseElementMeta):
    def __new__(cls, name: str, parameter_type: Any, required: bool, *parameters) -> type:
        return super().__new__(cls, name, parameter_type, required, *parameters)

    def __init__(cls, name: str, parameter_type: Any, required: bool, *parameters) -> None:
        cls.element_type = ConfigElementType.SwitchableElement
        super().__init__(name, parameter_type, required, *parameters)

    def copy(cls, name):
        if name == cls.__name__:
            raise HostrayWebException(109, name)
        new_cls = ConfigSwitchableElementMeta(
            name, cls.parameter_type, cls.required, *cls._cls_parameters.values())
        return new_cls


HostrayWebConfigRootValidator = ConfigContainerMeta(
    'root', True,
    ConfigElementMeta('name', str, False),
    ConfigElementMeta('port', int, False),
    ConfigElementMeta('debug', bool, True),
    ConfigElementMeta('cookie_secret', str, False),
    ConfigContainerMeta(
        'ssl', False,
        ConfigElementMeta('crt', str, True),
        ConfigElementMeta('key', str, True)
    )
)

HostrayWebConfigComponentValidator = ConfigContainerMeta(
    Component_Module_Folder, False,
    ConfigContainerMeta(
        'localization', False,
        ConfigElementMeta('dir', str, False),
        ConfigElementMeta('lang', str, False)
    ),
    ConfigContainerMeta(
        'logger', False,
        ConfigElementMeta('dir', str, True)
    ),
    ConfigContainerMeta(
        'task_queue', False,
        ConfigElementMeta('worker_count', int, True)
    ),
    ConfigContainerMeta(
        'worker_pool', False,
        ConfigScalableElementMeta(str, int)
    ),
    ConfigContainerMeta(
        'memory_cache', False,
        ConfigElementMeta('sess_lifetime', int, True),
        ConfigElementMeta('renew_lifetime', bool, False),
        ConfigElementMeta('renew_id', bool, False),
        ConfigElementMeta('save_file', str, False)),
    ConfigContainerMeta(
        'orm_db', False,
        ConfigScalableContainerMeta(
            str,
            ConfigSwitchableElementMeta(
                'module', str, True,
                ConfigContainerMeta(
                    'sqlite_memory', False,
                    ConfigElementMeta('worker', int, True),
                    ConfigElementMeta('connection_refresh', int, True)),
                ConfigContainerMeta(
                    'sqlite', False,
                    ConfigElementMeta('worker', int, True),
                    ConfigElementMeta('connection_refresh', int, True),
                    ConfigElementMeta('file_name', str, True)),
                ConfigContainerMeta(
                    'mysql', False,
                    ConfigElementMeta('worker', int, True),
                    ConfigElementMeta('connection_refresh', int, True),
                    ConfigElementMeta('host', str, True),
                    ConfigElementMeta('port', int, True),
                    ConfigElementMeta('db_name', str, True),
                    ConfigElementMeta('user', str, True),
                    ConfigElementMeta('password', str, True),
                ))
        )
    ),
    ConfigContainerMeta(
        'services', False,
        ConfigScalableContainerMeta(
            str,
            ConfigScalableContainerMeta(
                str,
                ConfigElementMeta('name', str, True),
                ConfigElementMeta('get', list, False),
                ConfigElementMeta('post', list, False),
                ConfigElementMeta('put', list, False),
                ConfigElementMeta('patch', list, False),
                ConfigElementMeta('delete', list, False)
            )
        )
    ),
)

HostrayWebConfigControllerValidator = ConfigContainerMeta(
    Controller_Module_Folder, False,
    ConfigScalableContainerMeta(
        str,
        ConfigElementMeta('enum', str, True),
        ConfigContainerMeta('params', False)
    )
)

HostrayWebConfigValidator = HostrayWebConfigRootValidator.copy('')
HostrayWebConfigValidator.set_cls_parameters(
    HostrayWebConfigComponentValidator)
HostrayWebConfigValidator.set_cls_parameters(
    HostrayWebConfigControllerValidator)
