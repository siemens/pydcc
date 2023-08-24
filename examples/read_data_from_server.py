# PyDCC
#
# Minimal working example
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Andreas Tobola, Siemens AG
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#
# SPDX-License-Identifier:  MIT
#
# Before starting this example, make sure to run the test server.
# dcc_test_server.py
#
import sys
sys.path.append("../dcc")
from dcc import DCC

# (1) Load DCC and create the DCC object (dcco)
dcco = DCC(url="http://127.0.0.1:8085/dcc/123")

# (2) Get UID of the DCC from DCC object
uid = dcco.uid()

# (3) Get days since last calibration from DCC object
days_since_calibration = dcco.days_since_calibration()

# (4) Print data
print('DCC UID: %s' % uid)
print('%d days since calibration' % days_since_calibration)
