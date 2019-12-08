# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Thursday, 14th November 2019 by hsky77 (howardlkung@gmail.com)
'''

from .request_controller import RequestController


class SystemAliveController(RequestController):
    async def get(self):
        self.write("1")


class ComponentsInfoController(RequestController):
    async def get(self):
        self.write({
            'name': self.settings['name'],
            'info': self.application.component_manager.info
        })
