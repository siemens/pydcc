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
import sys
sys.path.append("../dcc")
from dcc import DCC

# (1) Load DCC and create the DCC object (dcco)
dcco = DCC('../data/dcc/siliziumkugel_2_4_0.xml')

# (2) Get UID of the DCC from DCC object
uid = dcco.uid()

# (3) Get days since last calibration from DCC object
days_since_calibration = dcco.days_since_calibration()

# (4) Print data
print('DCC UID: %s' % uid)
print('%d days since calibration' % days_since_calibration)
