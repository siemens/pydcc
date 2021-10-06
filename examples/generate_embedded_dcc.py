# PyDCC
#
# Example script for generating an compressed DCC using PyDCC
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Andreas Tobola <andreas.tobola@siemens.com>
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#
import sys
sys.path.append("../src/")
from dcc import dcc


# (1) Load DCC from XML file
xml_file_name = '../data/dcc/siliziumkugel_2_4_0.xml' # Example from PTB
dcco = dcc(xml_file_name) # Load DCC and crate DCC object
calib_date = dcco.calibration_date()
print("Embedded DCC generation for constraint devices")

# (2) Generate compressed DCC
embdcc = dcco.generate_compressed_dcc()   
compression_ratio_100 = embdcc['compression_ratio'] * 100
print('DCC size %d bytes' % embdcc['bytes_uncompressed'])
print('Compressed DCC size %d bytes' % embdcc['bytes_compressed'])
print('CRC32 of raw data: %x' % embdcc['crc32'])
print('Embedded DCC compression ratio %.1f%%' % compression_ratio_100)


# (3) Write compressed DCC to file
compressed_dcc_filename = "../data/siliziumkugel_compressed.pydcc"
with open(compressed_dcc_filename, "wb") as f:
    f.write(embdcc['dcc_xml_raw_data_compressed'])


# (4) Load compressd DCC from file
with open(compressed_dcc_filename, "rb") as f:
            compressed_dcc_byte_array = f.read()
dcco2 = dcc(compressed_dcc = compressed_dcc_byte_array)
uid = dcco2.uid()
days_since_calibration = dcco2.days_since_calibration()
print('DCC UID: %s' % uid)
print('%d days since calibration' % days_since_calibration)


# (5) Additionally, write header file for C compiler.
c_array = embdcc['compressed_dcc_data_in_c']
#print(c_array[:102] + " ...")
with open("../data/siliziumkugel_compressed.h", "w") as f:
    f.write(c_array)
