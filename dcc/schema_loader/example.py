# PyDCC
#
# Python module for processing of digital calibration certificates (DCC)
# according to https://www.ptb.de/dcc/
#
# Copyright (c) Siemens AG, 2022
#
# Authors:
#     Kai Mienert, PTB
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#

import schema_loader as sl

"""
use of the scheme downloader
config parameters should be changed in schema_downloader.py
"""

if __name__ == "__main__":

    # update schemas

    result = sl.update_schemas(raise_errors=True)
    if result:
        print("Success")
    else:
        print("Failure")

    # get path to schema files to parse or validate xml files

    dcc_version = "3.1.1"
    path = sl.get_abs_local_dcc_shema_path(dcc_version=dcc_version)
    if path is not None:
        print(path)
    else:
        print(f"found no dcc.xsd schema for version {dcc_version} of dcc")

    path = sl.get_abs_local_dsi_shema_path(dcc_version=dcc_version)
    if path is not None:
        print(path)
    else:
        print(f"found no dsi.xsd schema for version {dcc_version} of dcc")
