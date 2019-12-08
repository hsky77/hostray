# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Friday, 8th November 2019 by hsky77 (howardlkung@gmail.com)
'''

from typing import Dict, List, Any, Tuple

from .localization import LocalizedMessageException
from .constants import LocalCode_Not_HierarchyElementMeta_Subclass, LocalCode_No_Parameters, LocalCode_Parameters_No_Key


class HierarchyElementMeta(type):
    def set_cls_parameters(cls, *cls_parameters) -> None:
        for cls_parameter in cls_parameters:
            if not hasattr(cls, '_cls_parameters'):
                cls._cls_parameters = {}

            if issubclass(type(cls), HierarchyElementMeta):
                cls._cls_parameters[cls_parameter.__name__] = cls_parameter
            else:
                raise LocalizedMessageException(
                    LocalCode_Not_HierarchyElementMeta_Subclass, cls)

    def get_cls_parameter(cls, key_routes: str, delimeter='.') -> type:
        routes = key_routes.split(delimeter)
        temp = cls
        for key in routes:
            if hasattr(temp, '_cls_parameters'):
                if key in temp._cls_parameters:
                    temp = temp._cls_parameters[key]
                else:
                    raise LocalizedMessageException(
                        LocalCode_Parameters_No_Key, temp, key)
            else:
                raise LocalizedMessageException(
                    LocalCode_No_Parameters, temp)

        return temp
