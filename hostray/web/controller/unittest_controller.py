# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Wednesday, 13th November 2019 by hsky77 (howardlkung@gmail.com)
'''

from . import (RequestController, DBCSUDController, WebSocketController,
               StreamingDownloadController, StreamingFileUploadController, StreamingUploadController)

from ...util import GB
from ...unit_test.util_orm import TestAccessor


class TestController(RequestController):
    async def get(self):
        response = await self.invoke_service_async('test_www', 'get', text='你好')
        self.write(response.text + '\n')

        response = await self.invoke_service_async('test_api', 'post', value='你好')
        self.write(response.text + '\n')

        response = await self.invoke_service_async('test_api', 'put', value='你好')
        self.write(response.text + '\n')

        response = await self.invoke_service_async('test_api', 'delete', id='你好')
        self.write(response.text + '\n')

        if self.cache is not None:
            if 'count' not in self.cache:
                self.cache['count'] = 0
            else:
                self.cache['count'] += 1

            self.write(
                '中文 Hello World from test_controller, and cache: {}'.format(self.cache))

    async def post(self):
        self.write('I got this post value: {}'.format(
            self.get_body_argument('value')))

    async def put(self):
        self.write('I got this put value: {}'.format(
            self.get_body_argument('value')))

    async def delete(self):
        self.write('I got this id to delete: {}'.format(
            self.get_query_argument('id')))


class TestCUSDController(DBCSUDController):
    orm_db_accessor = TestAccessor()


class TestStreamDownloadController(StreamingDownloadController):
    async def _prepare_binary(self):
        self.set_header('Content-Disposition',
                        'attachment; filename=' + 'test.data')
        b = b''.ljust(1*GB, b'0')
        return b


class TestStreamUploadController(StreamingUploadController):
    async def prepare(self):
        self.buffer = []

    def _on_chunk_received(self, headers, chunk, bytes_size_received):
        self.buffer.append(chunk)

    def _on_data_received(self, headers, bytes_size_received):
        data = b''.join(self.buffer)
        if 'charset' in self.content_mime_options:
            data = data.decode(self.content_mime_options['charset'])
        self.write(data)


class TestWebsocketController(WebSocketController):
    live_web_sockets = set()

    def on_message(self, message):
        self.send_message(message)

    def open(self):
        self.set_nodelay(True)
        self.live_web_sockets.add(self)

    def on_close(self):
        self.live_web_sockets.remove(self)

    def send_message(self, message):
        removable = set()
        for ws in self.live_web_sockets:
            if not ws.ws_connection or not ws.ws_connection.stream.socket:
                removable.add(ws)
            else:
                ws.write_message(message)
        for ws in removable:
            self.live_web_sockets.remove(ws)
