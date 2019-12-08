# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Monday, 4th November 2019 by hsky77 (howardlkung@gmail.com)
'''


import logging
from threading import Lock
from typing import List


class HostrayLogger(logging.Logger):
    """
    customized Hostray logger to replace logging.Logger
        - defaultly add file handler
    """

    def __init__(self, name: str, level: int = logging.INFO):
        super().__init__(name, level)
        self.__file_handler = None
        self.lock = Lock()

    def set_output_directory(self, log_dir: str = None, mode: str = 'a', encoding: str = 'utf-8') -> None:
        from .utils import join_path

        log_dir = log_dir or ''
        log_file = join_path(log_dir, self.name + '.log')

        if not log_dir == '':
            import os
            if not os.path.isdir(log_dir):
                os.makedirs(log_dir)

        if self.__file_handler is not None and (
                not self.__file_handler.baseFilename == os.path.abspath(log_file)):
            self.close()

        if self.__file_handler is None:
            self.__file_handler = logging.FileHandler(
                log_file, mode=mode, encoding=encoding)
            self.__file_handler.setFormatter(logging.Formatter(
                '%(name)s - %(levelname)s - %(asctime)s %(message)s'))
            self.addHandler(self.__file_handler)

    def close(self) -> None:
        if self.__file_handler is not None:
            self.__file_handler.close()
            self.removeHandler(self.__file_handler)
            self.__file_handler = None

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        # need a lock when logging in multi-thread process
        try:
            self.lock.acquire()
            super()._log(level, msg, args, exc_info=exc_info, extra=extra, stack_info=stack_info)
        finally:
            self.lock.release()


logging.setLoggerClass(HostrayLogger)


def get_Hostray_logger(name: str, log_dir: str = None, mode: str = 'a',
                       encoding: str = 'utf-8', log_to_resource: bool = False) -> HostrayLogger:
    logger = logging.getLogger(name)
    if log_to_resource:
        logger.set_output_directory(log_dir, mode=mode, encoding=encoding)
    else:
        logger.close()
    return logger


def setting_loggers(names: List[str],  log_dir: str, mode: str = 'a', encoding: str = 'utf-8', log_to_resource: bool = False) -> None:
    for name in names:
        get_Hostray_logger(name, log_dir, mode, encoding,
                           log_to_resource)


def configure_colored_logging(loglevel: str = 'INFO', logger: HostrayLogger = None) -> None:
    """
    note: only call once at the beginning of program
    """
    import coloredlogs
    field_styles = coloredlogs.DEFAULT_FIELD_STYLES.copy()
    field_styles['asctime'] = {}
    level_styles = coloredlogs.DEFAULT_LEVEL_STYLES.copy()
    level_styles['debug'] = {}
    if logger is not None:
        coloredlogs.install(
            level=loglevel,
            use_chroot=False,
            fmt='%(asctime)s %(levelname)-8s %(name)s  - %(message)s',
            level_styles=level_styles,
            field_styles=field_styles,
            logger=logger)
    else:
        coloredlogs.install(
            level=loglevel,
            use_chroot=False,
            fmt='%(asctime)s %(levelname)-8s %(name)s  - %(message)s',
            level_styles=level_styles,
            field_styles=field_styles)
