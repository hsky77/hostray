# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Tuesday, 5th November 2019 by hsky77 (howardlkung@gmail.com)
'''

from .constants import *

from tornado.web import Finish

from hostray.util import BaseLocal, join_path, LocalizedMessageException, Localization, LocalizedMessageWarning
BaseLocal.import_csv([join_path(__path__[0], Localization_File)])

HttpLocal = Localization()
HttpLocal.import_csv([join_path(__path__[0], Localization_HttpFile)])


class HostrayWebException(LocalizedMessageException):
    """exception class for hostray.web module"""
    pass


class HostrayWebFinish(LocalizedMessageWarning, Finish):
    """warning class for hostray.web module"""
    pass
