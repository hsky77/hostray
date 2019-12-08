# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Monday, 4th November 2019 by hsky77 (howardlkung@gmail.com)
'''


from enum import Enum
from datetime import datetime
from . import LocalizedMessageException
from .constants import LocalCode_No_Valid_DT_FORMAT


class DATETIME_TYPE(Enum):
    PY = '%Y-%m-%d %H:%M:%S.%f'
    DTF1 = '%Y-%m-%dT%H:%M:%S.%f'
    DTF2 = '%Y-%m-%d %H:%M:%S.%f'
    DTF3 = '%Y/%m/%dT%H:%M:%S.%f'
    DTF4 = '%Y/%m/%d %H:%M:%S.%f'
    DT1 = '%Y-%m-%dT%H:%M:%S'
    DT2 = '%Y-%m-%d %H:%M:%S'
    DT3 = '%Y/%m/%dT%H:%M:%S'
    DT4 = '%Y/%m/%d %H:%M:%S'
    D1 = '%Y-%m-%d'
    D2 = '%Y-%m-%d'
    D3 = '%Y/%m/%d'
    D4 = '%Y/%m/%d'

    def str_to_dt(self, sdt: str) -> datetime:
        return datetime.strptime(sdt, self.value)

    def dt_to_str(self, dt: datetime) -> str:
        return dt.strftime(self.value)


def str_to_datetime(sdt: str) -> datetime:
    """try convert str to datetime with DATETIME_TYPE format until no exception"""
    for k in DATETIME_TYPE:
        try:
            return datetime.strptime(sdt, k.value)
        except:
            pass
    raise LocalizedMessageException(LocalCode_No_Valid_DT_FORMAT, sdt)


def datetime_to_str(dt: datetime, dt_type: DATETIME_TYPE = DATETIME_TYPE.PY) -> str:
    return dt.strftime(dt_type.value)


PY_DT_Converter = DATETIME_TYPE.PY
DOT_NET_DT_Converter = DATETIME_TYPE.DT1
