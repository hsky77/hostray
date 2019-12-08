# Copyright (C) 2019-Present the hostray authors and contributors
#
# This module is part of hostray and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php:

'''
Last Updated:  Sunday, 10th November 2019 by hsky77 (howardlkung@gmail.com)
'''

from .. import Module_Path
Hostray_Folder = Module_Path

# reserved folder names
Component_Module_Folder = 'component'
Controller_Module_Folder = 'controller'
Unittest_Module_Folder = 'unit_test'
Dependency_Folder = 'dependency'

# reserved file names
Localization_File = 'local.csv'
Localization_HttpFile = 'httplocal.csv'
Hostray_Web_Config_File = 'server_config.yaml'
Hostray_Web_Pack_File = 'pack.yaml'
Hostray_Web_Requirement_File = 'requirements.txt'

# server
LocalCode_Application_Closing = 100
LocalCode_Application_Closed = 101
LocalCode_Not_Subclass = 102
LocalCode_Folder_Not_Exist = 103

# server config
LocalCode_Parameter_Required = 120
LocalCode_Parameter_Type_Error = 121
LocalCode_Setup_Error = 122
LocalCode_Invalid_Parameter = 123

# components
LocalCode_Component_Duplicated_Key = 200
LocalCode_Failed_To_Load_Component = 201
LocalCode_Component_Type_Not_Exist = 202
LocalCode_Comp_Missing_Parameter = 203
LocalCode_Not_Accessor_Function = 204
LocalCode_No_DB_Module = 205
LocalCode_Not_Support_DB_Module = 206

# controllers' localization code
LocalCode_Failed_To_Load_Controller = 300
LocalCode_Missing_Required_Parameter = 301
LocalCode_Incorrect_Type = 302
LocalCode_Not_Valid_Column = 303

LocalCode_Cache_Expired = 310
LocalCode_Data_Added = 311
LocalCode_Data_Updated = 312
LocalCode_Data_Delete = 313
LocalCode_Data_No_Changed = 314
LocalCode_Data_Not_Exist = 315
LocalCode_Data_Added_Failed = 316

LocalCode_Upload_Success = 320
LocalCode_Connect_Failed = 321
