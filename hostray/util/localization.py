# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Monday, 4th November 2019 by hsky77 (howardlkung@gmail.com)
'''


import os

from enum import Enum
from typing import List, Dict, Tuple

from .utils import join_path
from .constants import LocalCode_No_Code, LocalCode_Duplicated_Code, LocalCode_Local_Pack_Parsing_Error


class Localization():
    """convert message to localized language message"""
    default_code = str(LocalCode_No_Code)

    def __init__(self, lang: str = 'en'):
        self.__mapping = {}
        self.__csvs = []
        self.set_language(lang)
        self.__languages = set()

    def set_language(self, lang: str) -> None:
        self.__lang = lang

    @property
    def current_language(self) -> str:
        return self.__lang

    def get_info(self) -> Dict:
        """return dict shows how many language avaliable and the codes loaded"""
        return {
            'current_language': self.current_language,
            'loaded_languages': list(self.__languages),
            'codes': len(self.__mapping),
            'files_loaded': self.__csvs
        }

    def import_csvs_from_directory(self, dir: str, encoding: str = 'utf-8') -> None:
        """import coded message from all csv files of indicated directory"""
        self.import_csv([join_path(dir, f) for f in os.listdir(
            dir) if '.csv' in f and os.path.isfile(join_path(dir, f))])

    def import_csv(self, files: List[str], encoding: str = 'utf-8') -> None:
        """import coded message from csv file"""
        import re
        for path in files:
            with open(path, 'r', encoding=encoding) as f:
                self.__csvs.append(path)
                lines = f.readlines()

                if len(lines) > 0:
                    langs = [x.replace('\n', '') for x in lines.pop(
                        0).split(',') if not 'code' in x]

                for line in lines:
                    line = [x for x in re.split(',"(.*?)"|,', line) if
                            x is not None and not x == '' and not x == '\n']
                    if not len(line) - 1 == len(langs):
                        raise Exception(self.get_message(
                            LocalCode_Local_Pack_Parsing_Error, path))
                    idx = 1
                    for lang in langs:
                        self.__languages.add(lang)
                        if not line[0] in self.__mapping:
                            self.__mapping[line[0]] = {}

                        if not lang in self.__mapping[line[0]]:
                            self.__mapping[line[0]][lang] = line[idx].replace(
                                '\n', '')
                        else:
                            raise Exception(self.get_message(
                                LocalCode_Duplicated_Code, line[0], lang.name))
                        idx = idx + 1

    def has_message(self, code: str) -> bool:
        code = str(code)
        return code in self.__mapping

    def get_message(self, code: str, *strings) -> str:
        """convert to localized message via code and following parameters"""
        code = str(code)
        if not self.__lang in self.__languages:
            raise Exception(
                'language: {}, code: {} does not exist'.format(self.__lang, code))

        if code in self.__mapping:
            try:
                return self.__mapping[code][self.__lang].format(*strings)
            except:
                raise Exception(
                    self.__mapping['3'][self.__lang].format(code, strings))
        else:
            return self.__mapping[self.default_code][self.__lang].format(self.__lang, code)


BaseLocal = Localization()


class LocalizedMessageException(Exception):
    """localized message exception class"""

    def __init__(self, code: int, *args):
        super().__init__(BaseLocal.get_message(code, *args))
        self.code = code
        self.code_args = args


class LocalizedMessageWarning(Exception):
    """localized message warning exception class"""

    def __init__(self, code: int, *args):
        super().__init__(BaseLocal.get_message(code, *args))
        self.code = code
        self.code_args = args
