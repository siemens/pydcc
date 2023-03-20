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


print(dcco.item_id())


def get_item_id_by_name(dcco, searched_name, searched_language = None, searched_issuer = None, ):
	id_list = dcco.item_id()['identifications']['identification']
	for id in id_list:
		names = id['name']['content']
		issuer = id['issuer']
		if searched_issuer is not None:
			if not issuer == searched_issuer:
				continue
		for name in names:
			language = name['@lang']
			if searched_language is not None:
				if not language == searched_language:
					continue
			name_text =  name['#text']
			if name_text == searched_name:
				value = id['value']
				return value
	return None


serial_number = get_item_id_by_name(dcco, 'Serial no.')

if serial_number is not None:
	print("Serial number: " + serial_number)
else:
	print("Serial number not found.")


serial_number = get_item_id_by_name(dcco, 'Serial no.', 'en')

if serial_number is not None:
	print("Serial number: " + serial_number)
else:
	print("Serial number not found.")


serial_number = get_item_id_by_name(dcco, 'Serial no.', 'en', 'manufacturer')

if serial_number is not None:
	print("Serial number: " + serial_number)
else:
	print("Serial number not found.")



#print(dcco.item_id()['identifications']['identification'])
#for elem in dcco.item_id()['identifications']['identification']:
#	print(elem)