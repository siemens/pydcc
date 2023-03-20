# PyDCC
#
# Python module for processing of digital calibration certificates (DCC)
# according to https://www.ptb.de/dcc/
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Andreas Tobola <andreas.tobola@siemens.com>
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#
import sys
sys.path.append("../dcc")
from dcc import DCC

xml_file_name = '../data/dcc/dcc_gp_temperature_typical_v12.xml'
dcco = DCC(xml_file_name) # Load DCC and crate DCC object

print('----ID---')
print(dcco.item_id())

#print(dcco.item_id()['identifications']['identification'])
for elem in dcco.item_id()['identifications']['identification']:
	print(elem)