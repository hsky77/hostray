# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Saturday, 7th December 2019 by hsky77 (howardlkung@gmail.com)
'''


from typing import Union, Dict, Any
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler

from .base import ControllerAddon


class WebSocketController(ControllerAddon, WebSocketHandler):
    def __init__(self, application, request, **kwds):
        ControllerAddon.__init__(self, application, request, **kwds)
        WebSocketHandler.__init__(self, application, request, **kwds)

        self.io_loop = IOLoop.current(False)

    def write_message(self, message: Union[bytes, str, Dict[str, Any]], binary: bool = False) -> "Future[None]":
        if IOLoop.current(False) is self.io_loop:
            try:
                return super().write_message(message, binary)
            except IOError:
                self.io_loop.add_callback(self.on_close)
        else:
            self.io_loop.add_callback(self.write, message, binary)
