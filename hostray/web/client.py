# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
This module provides client-side tool to communicate with web server.

    - WebSocketClient communicates with server in web socket, for example:

        with WebSocketClient() as c:
            c.connect('ws://localhost:8888/test_socket', lambda msg: print('received message: {}'.format(msg)))
            text = input().strip()
            while text is not 'q':
                c.write_message(text)
                text = input().strip()

    - StreamUploadClient is the data uploader via streaming http request. for exampe:

        with StreamUploadClient() as c:

            # send file
            c.send_file('http://localhost:8888/test_file_upload', 'test.py', 'test.py')

            # send some bytes
            c.send_bytes('http://localhost:8888/test_bytes_upload', b'000000000  weftest.py')

            # send string
            c.send_string('http://localhost:8888/test_bytes_upload', '000000000  weftest.py')

            # send with generator
            def gen():
                for i in range(20):
                    yield str(i).encode('utf-8')

            c.send_by_generator('http://localhost:8888/test_bytes_upload', gen(), encoding='utf-8')

            # async
            loop = asyncio.new_event_loop()

            loop.run_until_complete(c.send_file_async(
                'http://localhost:8888/test_file_upload', 'test.py', 'test.py'))

            loop.run_until_complete(c.send_bytes_async(
                'http://localhost:8888/test_bytes_upload', b'wefwefwegge  weftest.py'))
            
            loop.run_until_complete(c.send_string_async(
                'http://localhost:8888/test_bytes_upload', 'wefwefwegge  weftest.py'))

            loop.run_until_complete(c.send_by_generator_async(
                'http://localhost:8888/test_bytes_upload', gen(), encoding='utf-8'))

Last Updated:  Tuesday, 5th November 2019 by hsky77 (howardlkung@gmail.com)
'''

import os
import time
import asyncio
import requests

from typing import Callable, ByteString, Generator, Union, Dict, Any

from tornado.ioloop import IOLoop

from hostray.util import Worker, FunctionLoopWorker, KB
from . import HostrayWebException, LocalCode_Connect_Failed


class WebSocketClient(FunctionLoopWorker):
    def __init__(self, name: str = None, reconnect: int = 3):
        super().__init__(name, 0)
        self.conn = None
        self.reconnect = reconnect

    def dispose(self):
        self.disconnect()
        super().dispose()

    @property
    def is_connected(self):
        return self.conn is not None

    def connect(self, url: str, on_message_callback: Callable = None):
        if self.conn is None:
            self.url = url
            self.connect_count = 0
            self.on_message_callback = on_message_callback
            self.run_method(self._start)

            while not self.is_connected and self.connect_count < self.reconnect:  # wait for connected
                import time
                time.sleep(0)

            if not self.is_connected:
                raise HostrayWebException(LocalCode_Connect_Failed, self.url)

    async def connect_async(self, url: str, on_message_callback: Callable = None):
        if self.conn is None:
            self.url = url
            self.connect_count = 0
            self.on_message_callback = on_message_callback
            self.run_method(self._start)

            while not self.is_connected and self.connect_count < self.reconnect:  # wait for connected
                import asyncio
                await asyncio.sleep(0)

            if not self.is_connected:
                raise HostrayWebException(LocalCode_Connect_Failed, self.url)

    def disconnect(self):
        if self.conn is not None:
            if IOLoop.current(False) is self.io_loop:
                try:
                    self.conn.close()
                    self.conn = None
                except IOError:
                    pass
                finally:
                    self.stop()
            else:
                self.io_loop.add_callback(self.disconnect)

    def write_message(self, message: Union[str, bytes], binary: bool = False) -> None:
        if self.conn is not None:
            if IOLoop.current(False) is self.io_loop:
                try:
                    self.conn.write_message(message)
                except IOError:
                    self.io_loop.add_callback(self.disconnect)
            else:
                self.io_loop.add_callback(
                    self.conn.write_message, message, binary)

    def _start(self):
        import asyncio
        if self.connect_count < self.reconnect:
            try:
                loop = asyncio.new_event_loop()
                loop.run_until_complete(self.__run())
            finally:
                self.connect_count = self.connect_count + 1

    async def __run(self):
        from tornado.websocket import websocket_connect
        self.conn = await websocket_connect(self.url)
        self.io_loop = IOLoop.current(False)
        msg = await self.conn.read_message()
        while msg is not None:
            if callable(self.on_message_callback):
                self.on_message_callback(msg)
            msg = await self.conn.read_message()


class StreamUploadClient(Worker):
    def send_file(self, url: str, source: str, target: str, chunk_size: int = 4*KB,
                  on_chunk_send: Callable[[int, int], None] = None) -> requests.Response:
        return self.run_method_and_wait(self._send_file, url, source,
                                        target, chunk_size, on_chunk_send)

    async def send_file_async(self, url: str, source: str, target: str, chunk_size: int = 4*KB,
                              on_chunk_send: Callable[[int, int], None] = None) -> requests.Response:
        return await self.run_method_and_wait_async(self._send_file, url, source,
                                                    target, chunk_size, on_chunk_send)

    def _send_file(self, url: str, source: str, target: str, chunk_size: int = 4*KB,
                   on_chunk_send: Callable[[int, int], None] = None) -> requests.Response:
        statinfo = os.stat(source)
        headers = {"Content-Type": "application/octet-stream",
                   "filename": target}
        with open(source, 'rb') as f:
            response = requests.put(url, data=self.__send(
                f, chunk_size, on_chunk_send, statinfo.st_size), headers=headers)
            response.close()
            return response

    def send_bytes(self, url: str, data: ByteString, chunk_size: int = 4*KB,
                   on_chunk_send: Callable[[int, int], None] = None, encoding: str = None) -> requests.Response:
        return self.run_method_and_wait(self._send_bytes, url, data,
                                        chunk_size, on_chunk_send, encoding)

    async def send_bytes_async(self, url: str, data: ByteString, chunk_size: int = 4*KB,
                               on_chunk_send: Callable[[int, int], None] = None, encoding: str = None) -> requests.Response:
        return await self.run_method_and_wait_async(self._send_bytes, url, data,
                                                    chunk_size, on_chunk_send, encoding)

    def send_string(self, url: str, data: str, chunk_size: int = 4*KB,
                    on_chunk_send: Callable[[int, int], None] = None, encoding: str = 'utf-8') -> requests.Response:
        return self.send_bytes(url, data.encode(encoding), chunk_size, on_chunk_send, encoding)

    async def send_string_async(self, url: str, data: str, chunk_size: int = 4*KB,
                                on_chunk_send: Callable[[int, int], None] = None, encoding: str = 'utf-8') -> requests.Response:
        return await self.send_bytes_async(url, data.encode(encoding), chunk_size, on_chunk_send, encoding)

    def _send_bytes(self, url: str, data: ByteString, chunk_size: int = 4*KB,
                    on_chunk_send: Callable[[int, int], None] = None, encoding: str = None) -> requests.Response:
        from io import BytesIO
        content_type = "application/octet-stream"
        if encoding is not None:
            content_type = content_type + "; charset={}".format(encoding)

        headers = {"Content-Type": content_type}
        response = requests.post(url, data=self.__send(
            BytesIO(data), chunk_size, on_chunk_send, len(data)), headers=headers)
        response.close()
        return response

    def send_by_generator(self, url: str, generator: Generator, encoding: str = None) -> requests.Response:
        return self.run_method_and_wait(self._send_by_generator, url, generator, encoding)

    async def send_by_generator_async(self, url: str, generator: Generator, encoding: str = None) -> requests.Response:
        return await self.run_method_and_wait_async(self._send_by_generator, url, generator, encoding)

    def _send_by_generator(self, url: str, generator: Generator, encoding: str = None) -> requests.Response:
        content_type = "application/octet-stream"
        if encoding is not None:
            content_type = content_type + "; charset={}".format(encoding)

        headers = {"Content-Type": content_type}
        response = requests.post(url, data=generator, headers=headers)
        response.close()
        return response

    def __send(self, io_stream, chunk_size, on_chunk_send, total_length):
        from functools import partial
        bytes_send = 0
        for chunk in iter(partial(io_stream.read, chunk_size), b''):
            yield chunk
            bytes_send = bytes_send + len(chunk)
            if callable(on_chunk_send):
                on_chunk_send(bytes_send, total_length)
