# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Tuesday, 5th November 2019 by hsky77 (howardlkung@gmail.com)
'''

import os
import math
import asyncio
import cgi

from tornado.web import stream_request_body

from hostray.util import join_path, FunctionQueueWorker, KB, MB, GB, TB

from .. import HostrayWebFinish
from .request_controller import LocalCode_Missing_Required_Parameter, RequestController
from .. import LocalCode_Upload_Success


class StreamingDownloadController(RequestController):
    SUPPORTED_METHODS = ("GET", "OPTIONS")

    def initialize(self, chunk_size: int = 4*KB, **kwds):
        self.chunk_size = chunk_size

    async def _prepare_binary(self):
        raise NotImplementedError()

    async def get(self):
        bdata = await self._prepare_binary()
        self.set_header('Content-Type', 'application/octet-stream')

        for i in range(0, math.ceil(len(bdata) / self.chunk_size)):
            start = i * self.chunk_size
            data = bdata[start:min(start+self.chunk_size, len(bdata))]
            self.write(data)
            await asyncio.sleep(0)

        self.finish()


@stream_request_body
class StreamingUploadController(RequestController):
    SUPPORTED_METHODS = ("POST", "PUT", "OPTIONS")

    def initialize(self, upload_dir: str = '', max_stream_size: int = 1*GB,  **kwds):
        self.upload_dir = join_path(self.root_dir, upload_dir)
        self.request.connection.set_max_body_size(max_stream_size)

        self._data_worker = FunctionQueueWorker()
        self.content_mime_type, self.content_mime_options = cgi.parse_header(
            self.request.headers['Content-Type'])

        self.bytes_length = 0

    async def prepare(self):
        pass

    async def data_received(self, chunk):
        self.bytes_length = self.bytes_length + len(chunk)
        self._data_worker.run_method(
            self._on_chunk_received, self.request.headers, chunk, self.bytes_length)

    async def post(self):
        while not self._data_worker.pending_count == 0:
            await asyncio.sleep(0)
        self._data_worker.dispose()
        await self.run_method_async(self._on_data_received, self.request.headers, self.bytes_length)

    async def put(self):
        while not self._data_worker.pending_count == 0:
            await asyncio.sleep(0)
        self._data_worker.dispose()
        await self.run_method_async(self._on_data_received, self.request.headers, self.bytes_length)

    def _on_chunk_received(self, headers, chunk, bytes_size_received):
        raise NotImplementedError()

    def _on_data_received(self, headers, bytes_size_received):
        pass

    def _handle_request_exception(self, e: BaseException) -> None:
        self._data_worker.dispose()
        super()._handle_request_exception(e)


class StreamingFileUploadController(StreamingUploadController):
    async def prepare(self):
        await super().prepare()
        self.filename = self.request.headers.get("filename")
        if self.filename is None:
            raise HostrayWebFinish(
                LocalCode_Missing_Required_Parameter, 'filename')

        path = join_path(self.upload_dir, self.filename)

        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        self.__file = open(path, 'wb')

    def _on_chunk_received(self, headers, chunk, bytes_size_received):
        if self.__file is not None:
            self.__file.write(chunk)

    def _on_data_received(self, headers, bytes_size_received):
        if self.__file is not None:
            self.__file.close()
            self.__file = None

            self.log_info(self.get_localized_message(
                LocalCode_Upload_Success, self.filename))
            self.write(self.get_localized_message(
                LocalCode_Upload_Success, self.filename))
