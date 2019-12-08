# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
This module wraps threading.Thread to execute functions:
    - Worker: executes function once
    - FunctionLoopWorker: looping a single function before calling stop()
    - FunctionQueueWorker: queue functions to be executed (FIFO)

    - WorkerPool: pooling the workers to execute function once, the workers could be reserved to run multiple functions
    - AsyncWorkerPool: inherit from WorkerPool, allow execute functions asynchronously

    note: run_method() of WorkerPool and AsyncWorkerPool blocks the main thread

Last Updated:  Monday, 4th November 2019 by hsky77 (howardlkung@gmail.com)
'''

from .worker import Worker, FunctionLoopWorker, FunctionQueueWorker
from .pool import WorkerPool, AsyncWorkerPool, PoolWorkerExecutor
