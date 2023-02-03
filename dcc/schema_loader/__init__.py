# PyDCC
#
# Python module for processing of digital calibration certificates (DCC)
# according to https://www.ptb.de/dcc/
#
# Copyright (c) Siemens AG, 2022
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#

from .schema_loader import update_schemas
from .schema_loader import get_abs_local_dcc_shema_path
from .schema_loader import get_abs_local_dsi_shema_path
