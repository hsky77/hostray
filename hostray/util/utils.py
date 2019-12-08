# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Monday, 4th November 2019 by hsky77 (howardlkung@gmail.com)
'''


import os

from typing import List, Dict


def get_class(module: str, *attrs):
    """cls = get_class("module", "class / static function", "class static function")"""
    from importlib import import_module
    cls = import_module(module)
    for a in attrs:
        cls = getattr(cls, a)
    return cls


def join_to_abs_path(*paths) -> str:
    """os.path.join() + os.path.abspath() to return only linux path string, that means replace '\\' with '/'"""
    return os.path.abspath(os.path.join(*paths)).replace('\\', '/')


def join_path(*paths) -> str:
    """os.path.join() to return only linux path string, that means replace '\\' with '/'"""
    return os.path.join(*paths).replace('\\', '/')


def walk_to_file_paths(file_or_directory: str) -> List[str]:
    """get a list of absolutely path from the input path recursively"""
    file_paths = []
    if os.path.isdir(file_or_directory):
        for root, _, files in os.walk(file_or_directory):
            for i in range(len(files)):
                files[i] = join_path(os.path.abspath(root), files[i])

            if len(files) > 0:
                file_paths.extend(files)
    elif os.path.isfile(file_or_directory):
        file_paths.append(file_or_directory)

    return file_paths


def size_bytes_to_string(f_size: int, units: List[str] = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB']) -> str:
    """return byte size string in unit"""
    index = 0
    while int(f_size / 1024) > 0:
        if index >= (len(units)-1):
            break
        f_size = f_size / 1024
        index = index + 1
    return '{:.1f} {}'.format(f_size, units[index])


def generate_base64_uid(byte_length: int = 32, urlsafe: bool = True) -> str:
    """generate customized uuid string"""
    import uuid
    import base64
    uid = uuid.uuid1().bytes
    uid = uid + os.urandom(byte_length-len(uid))
    if urlsafe:
        session_id = base64.urlsafe_b64encode(uid)
    else:
        session_id = base64.b64encode(uid)
    return session_id.decode('utf-8')


def convert_tuple_to_dict(t: tuple, key_name: str) -> Dict:
    """
    d = convert_tuple_to_dict((1, 2, 3), 'n'))

    # d is {'n_1': 1, 'n_2': 2, 'n_3': 3}
    """
    res = {}
    if t is not None:
        length = 0
        while len(t) > length:
            res['{}_{}'.format(key_name, str(length+1))] = t[length]
            length = length + 1
    return res


def get_host_ip(remote_host: str = '8.8.8.8', port: int = 80) -> str:
    """use this function to get the host ip, no guarantee"""
    import socket
    ip = socket.gethostbyname(socket.gethostname())
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((remote_host, port))
        ip = s.getsockname()[0]
    except:
        ip = socket.gethostbyname(socket.gethostname())
    finally:
        s.close()

    return ip
