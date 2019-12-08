# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Tuesday, 5th November 2019 by hsky77 (howardlkung@gmail.com)
'''

import os
import re
import sys
from typing import List, Set, ByteString, Tuple

from hostray.util import walk_to_file_paths, join_path, configure_colored_logging
from hostray.web.server import HostrayServer

from . import Dependency_Folder, Hostray_Web_Pack_File, Hostray_Web_Requirement_File


class HostrayPack(object):
    """
    pack server files to compressed output file, .zip for windows os and tar.gz for the others
    """

    default_exclude_keys = ['__pycache__']

    def pack(self, server_folder: str, output_file_path: str, prepare_wheels: bool = False,
             compile_py: bool = True, log_level: str = 'INFO'):
        configure_colored_logging(log_level)

        if output_file_path is None:
            file_name = os.path.basename(os.path.normpath(server_folder))
            if sys.platform == 'win32':
                output_file_path = 'win_' + file_name + '.zip'
            else:
                output_file_path = 'linux_' + file_name + '.tar.gz'

        # create packing file paths
        paths, py_paths, requirements = self._create_file_paths(server_folder)

        # get wheel dependencies
        if prepare_wheels:
            for req in requirements:
                if os.path.isfile(req):
                    self._preparing_python_wheels(Dependency_Folder, req)
            paths.update(walk_to_file_paths(Dependency_Folder))

        # add arc path for iterable paths as [(path, arcpath)]
        paths = self._setup_arc_paths(paths, server_folder)
        py_paths = self._setup_arc_paths(py_paths, server_folder)
        requirements = self._setup_arc_paths(requirements, server_folder)

        # making ouput file
        self._packing_files(
            paths, py_paths, output_file_path, compile_py=compile_py)

    def _setup_arc_paths(self, paths: str, server_folder: str):
        new_paths = []
        server_folder = os.path.dirname(server_folder)
        for path in paths:
            m = re.match('(.*):/', path)
            if m:
                path = path.replace(path[m.start():m.end()],
                                    path[m.start():m.end()].upper())

            arc_path = path.replace(server_folder, '')
            arc_path = arc_path[1:] if arc_path[0] == '/' else arc_path
            new_paths.append((path, arc_path))
        return new_paths

    def _create_file_paths(self, server_folder: str) -> Tuple[Set[str], Set[str], Set[str]]:
        import yaml
        print('creating packing list...')
        paths = set()
        py_paths = set()
        requirement_paths = set()

        hostray_exclude = self.default_exclude_keys
        for directory in [server_folder]:
            sub_paths = set()
            pack_list = join_path(directory, Hostray_Web_Pack_File)
            if os.path.isfile(pack_list):
                with open(pack_list, 'r') as f:
                    config = yaml.load(f, Loader=yaml.SafeLoader)
                    config = config if config else {}

                    if 'include' in config:
                        if config['include'] is not None:
                            for path in config['include']:
                                if os.path.isdir(path):
                                    ps, pys, rs = self._create_file_paths(path)
                                    paths.update(ps)
                                    py_paths.update(pys)
                                    requirement_paths.update(rs)
                                else:
                                    sub_paths.add(path)

                    sub_paths.update(walk_to_file_paths(directory))

                    if 'exclude' in config:
                        if config['exclude'] is not None:
                            exclude = hostray_exclude + config['exclude']
                        else:
                            exclude = hostray_exclude
                    exclude.append(pack_list)

                    py_paths.update([p for p in sub_paths if '.py' in p and max(
                        [p.find(x) for x in exclude]) == -1])
                    paths.update([p for p in sub_paths if not '.py' in p and max(
                        [p.find(x) for x in exclude]) == -1])
            else:
                # if pack setting file does not exist, collect all files under the server folder
                sub_paths = walk_to_file_paths(directory)
                paths.update([p for p in sub_paths if not '.py' in p and max(
                    [p.find(x) for x in hostray_exclude]) == -1])
                py_paths.update([p for p in sub_paths if '.py' in p and max(
                    [p.find(x) for x in hostray_exclude]) == -1])

            requirement_paths.add(
                join_path(directory, Hostray_Web_Requirement_File))

        return paths, py_paths, requirement_paths

    def _preparing_python_wheels(self, dependency_folder: str, requirements: str) -> None:
        """using pip to download python packages for later packing"""
        import subprocess

        print('clean dependency folder')
        self.__remove_dir(dependency_folder)

        # build wheels
        if sys.platform == 'win32':
            command = 'python'
        else:
            command = 'python3'
        print('preparing pip wheels...')
        res = subprocess.run([command, '-m', 'pip', 'wheel', '-w',
                              dependency_folder, '-r', requirements])

        if res.returncode > 0:
            raise Exception('getting pip wheels failed...')

    def _packing_files(self, paths: List[str], py_paths: List[str], output_path: str, compile_py: bool = True) -> None:
        if len(paths) > 0:
            if sys.platform == 'win32':
                import zipfile
                with zipfile.ZipFile(output_path, mode='w') as zf:
                    for path in paths:
                        print('packing file: {}'.format(path[0]))
                        zf.write(path[0], arcname=path[1])

                    for path in py_paths:
                        if compile_py:
                            bytecode = self.__get_compiled_py_bytecode(path[0])
                            zf.writestr(path[1].replace(
                                '.py', '.pyc'), bytecode)
                        else:
                            print('packing py file: {}'.format(path[0]))
                            zf.write(path[0], arcname=path[1])
            else:
                import tarfile
                from io import BytesIO
                with tarfile.open(output_path, mode='w:gz') as tarf:
                    for path in paths:
                        print('packing file: {}'.format(path))
                        tarf.add(path[0], arcname=path[1])

                    for path in py_paths:
                        if compile_py:
                            bytecode = self.__get_compiled_py_bytecode(path[0])
                            bIO = BytesIO()
                            bIO.write(bytecode)
                            bIO.seek(0)
                            info = tarfile.TarInfo(
                                name=path[1].replace('.py', '.pyc'))
                            info.size = len(bIO.getbuffer())
                            tarf.addfile(tarinfo=info, fileobj=bIO)
                        else:
                            print('packing py file: {}'.format(path[0]))
                            tarf.add(path[0], arcname=path[1])
        else:
            print('Warning: no file had been packed to {}'.format(output_path))

    def __remove_dir(self, dir: str) -> None:
        from shutil import rmtree
        try:
            rmtree(dir)
        except:
            pass

    def __get_compiled_py_bytecode(self, path: str) -> ByteString:
        import importlib
        print('compiling and packing python file: {}'.format(path))
        loader = importlib.machinery.SourceFileLoader(
            '<hostray_compiled>', path)
        source_bytes = loader.get_data(path)
        code = compile(source_bytes, path,
                       'exec', dont_inherit=True)
        source_stats = loader.path_stats(path)
        bytecode = importlib._bootstrap_external._code_to_bytecode(
            code, source_stats['mtime'], source_stats['size'])
        return bytecode
