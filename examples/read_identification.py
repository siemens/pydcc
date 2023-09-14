# PyDCC
#
# Python module for processing of digital calibration certificates (DCC)
# according to https://www.ptb.de/dcc/
#
# Copyright (c) Siemens AG, 2023
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

xml_file_name = '../data/dcc/dcc_gp_temperature_typical_v12.xml'
dcco = DCC(xml_file_name) # Load DCC and crate DCC object


print(dcco.item_id())

def print_serial_number(serial_number):
	if serial_number is not None:
		print("Serial number: " + serial_number)
	else:
		print("Serial number not found.")

# A search string can be specified. The first match will be returned.
serial_number = dcco.get_item_id_by_name('Serial no.')
print_serial_number(serial_number)

serial_number = dcco.get_item_id_by_name('Serial no.', 'en')
print_serial_number(serial_number)

serial_number = dcco.get_item_id_by_name('Serial no.', 'en', 'manufacturer')
print_serial_number(serial_number)

serial_number = dcco.get_item_id_by_name('Serien Nr.')
print_serial_number(serial_number)

serial_number = dcco.get_item_id_by_name('Seriennummer')
print_serial_number(serial_number)