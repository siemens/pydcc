# PyDCC
#
# Minimal working example
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#
# SPDX-License-Identifier:  MIT
#
import sys
import zlib
import sys
sys.path.append("../dcc")
from dcc import DCC

# (1) Load DCC and create the DCC object (dcco)
dcco = DCC('../data/dcc/dcc_gp_temperature_typical_v12.xml')

print("alle Resultate mit Namen auf deutsch, wenn möglich")
res = dcco.get_calibration_results('name', 'de')
for i in res:
   print(i)


print("alle Resultate mit  zugehörigen Xpath-Ausdrücken ")
res = dcco.get_calibration_results('xpath', 'de')
for i in res:
   print(i)