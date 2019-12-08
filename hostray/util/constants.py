# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Sunday, 10th November 2019 by hsky77 (howardlkung@gmail.com)
'''

KB = 1024
MB = 1024 * KB
GB = 1024 * MB
TB = 1024 * GB

Localization_File = 'local.csv'

LocalCode_No_Code = 0                                   # args: (str, str)
LocalCode_Duplicated_Code = 1                           # args: (str, str)
LocalCode_Local_Pack_Parsing_Error = 2                  # args: (str)

LocalCode_Not_Async_Gen = 10                            # args: ()
LocalCode_Not_Yield = 11                                # args: ()
LocalCode_Not_Stop = 12                                 # args: ()
LocalCode_Not_Stop_After_Throw = 13                     # args: ()

LocalCode_Not_Valid_Enum = 20                           # args: (Union[Enum, str], Enum)
LocalCode_Not_ASYNC_FUNC = 21                           # args: (Callable)

LocalCode_No_Valid_DT_FORMAT = 31                       # args: (str)

LocalCode_Must_Be_3Str_Tuple = 40                       # args: ()
LocalCode_Must_Be_Class = 41                            # args: (Type)
LocalCode_Must_Be_Function = 42                         # args: (Callable)
LocalCode_Is_Not_Subclass = 43                          # args: (child_cls, parent_cls)

LocalCode_Missing_File_Path: int = 50                   # args: ()
LocalCode_Missing_Host: int = 51                        # args: ()
LocalCode_Missing_User: int = 52                        # args: ()
LocalCode_Missing_Password: int = 53                    # args: ()
LocalCode_Missing_DB_Name: int = 54                     # args: ()

LocalCode_Not_Allow_Update: int = 55                    # args: (str)
LocalCode_Must_Be_Type: int = 56                        # args: (str, Type)
LocalCode_Invalid_Column: int = 57                      # args: (str)

LocalCode_Not_HierarchyElementMeta_Subclass = 90        # args: (str)
LocalCode_No_Parameters = 91                            # args: (type)
LocalCode_Parameters_No_Key = 92                        # args: (type, str)
