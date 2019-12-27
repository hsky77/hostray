# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
This module contains the "yaml" configurable component classes for hostray application.

    - order to load components of hostray application are followings:
        
        1. load the components of DefaultComponentTypes

        2. initailize the components of DefaultComponentTypes with "server_config.yaml" if specified or default settings

        3. check whether "server_config.yaml" specified components of OptionalComponentTypes to load

        4. check whether "server_config.yaml" specified components of extension module to load    

    - to create component extension module:

        0. the hierarchy of folders and files looks like:

            server_directory/
                server_config.yaml
                component/
                    __init__.py
                    foo.py

        1. use ComponentTypes enum class to define the extend components such as:

            class ComponentExtension(ComponentTypes):
                # tuple(<component_key>, <package_route>, <class_name_in_the_py_file>)

                Foo = ('foo', 'foo', 'Foo')

        2. in "foo.py" contains the class code:

            from hostray.web.component import Component, ComponentManager
            from . import ComponentExtension

            class Foo(Component):
                def __init__(self):
                    super().__init__(ComponentExtension.Foo)

                def init(self, component_manager: ComponentManager, p1, *arugs, **kwargs) -> None:
                    self.p1 = p1

        3. setup component block of "server_config.yaml" to tell hostray server load the extend components "Foo":

            component:              # block to setup component
                foo:                # component_key to load
                    p1: xxxx        # parameter p1 of Foo.init()

Last Updated:  Monday, 4th November 2019 by hsky77 (howardlkung@gmail.com)
'''

from typing import Dict, List, Union

from .base import ComponentTypes, Component, ComponentManager
from .. import HostrayWebException, LocalCode_Component_Duplicated_Key, LocalCode_Failed_To_Load_Component


class DefaultComponentTypes(ComponentTypes):
    """server loads all components of this enum type when start"""

    Localization = ('localization', 'default_component',
                    'LocalizationComponent')
    Logger = ('logger', 'default_component', 'LoggerComponent')
    Callback = ('callback', 'default_component', 'CallbackComponent')
    WorkerPool = ('worker_pool', 'default_component', 'WorkerPoolComponent')
    TaskQueue = ('task_queue', 'default_component', 'TaskQueueComponent')


class OptionalComponentTypes(ComponentTypes):
    """server loads configured components of this enum type when start"""

    Service = ('services', 'optional_component', 'ServicesComponent')
    MemoryCache = ('memory_cache', 'optional_component',
                   'MemoryCacheComponent')
    OrmDB = ('orm_db', 'optional_component', 'OrmDBComponent')


def __create_optional_components(component_manager: ComponentManager, component_settings: Dict, component_types: ComponentTypes, root_dir: str) -> None:
    for key in component_settings:
        for component_type in component_types:
            comp_type = None
            try:
                comp_type = component_type(key)
            except:
                continue
            if comp_type is not None:
                comp = comp_type.import_class()(comp_type)
                component_manager.set_component(comp)
                break

    for key in component_settings:
        comp_type = None
        for component_type in component_types:
            try:
                comp_type = component_type(key)
                break
            except:
                continue

        if comp_type:
            component_manager.invoke(comp_type, 'init',
                                     component_manager,
                                     **(component_settings[comp_type.enum_key] or {}),
                                     root_dir=root_dir)


def create_server_component_manager(component_settings: Union[Dict, None], root_dir: str,
                                    option_component_types: List[ComponentTypes] = [OptionalComponentTypes]) -> ComponentManager:
    component_manager = ComponentManager()

    # default components
    for default_type in DefaultComponentTypes:
        comp = default_type.import_class()(default_type)
        component_manager.set_component(comp)

    # init
    for default_type in DefaultComponentTypes:
        if component_settings and default_type.enum_key in component_settings:
            component_manager.invoke(default_type, 'init',
                                     component_manager,
                                     **(component_settings[default_type.enum_key] or {}),
                                     root_dir=root_dir)
        else:
            component_manager.invoke(
                default_type, 'init', component_manager, root_dir=root_dir)

    # optional components
    if component_settings:
        __create_optional_components(
            component_manager, component_settings, [OptionalComponentTypes], root_dir)

    sort_types = [OptionalComponentTypes, DefaultComponentTypes]
    # extensions
    ext_comp_types = ComponentTypes.get_component_enum_class()
    if ext_comp_types is not None:
        sort_types = ext_comp_types + \
            [OptionalComponentTypes, DefaultComponentTypes]

        # check duplicated key:
        for r_type in sort_types:
            for key in r_type:
                for l_type in sort_types:
                    d_key = None
                    if r_type is not l_type:
                        try:
                            d_key = l_type(key.enum_key)
                        except:
                            continue
                    if d_key is not None:
                        raise HostrayWebException(
                            LocalCode_Component_Duplicated_Key, l_type, r_type, key.enum_key)

        if component_settings:
            __create_optional_components(
                component_manager, component_settings, ext_comp_types, root_dir)

    # check componet load failed
    if component_settings:
        for key in component_settings:
            checked = False
            for component in component_manager.components:
                if key == component.component_type.enum_key:
                    checked = True
            if not checked:
                raise HostrayWebException(
                    LocalCode_Failed_To_Load_Component, root_dir, key)

    # sort with enums order
    component_manager.sort_components(sort_types)

    return component_manager
