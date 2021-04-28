# PyDCC
#
# Python module for processing of digital calibration certificates (DCC)
# according to https://www.ptb.de/dcc/
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

xml_file_name = '../data/dcc/siliziumkugel_2_4_0.xml' # Example from PTB
dcco = dcc(xml_file_name) # Load DCC and crate DCC object
#try:
    #if dcco.verify_dcc_xml():
    #    print("XML schema is valid.")
    #else:
    #    print("XML schema is invalid.")
#except Exception as inst:
#    print("XML schema not verified.")

calib_date = dcco.calibration_date()
print('Calibration date: %s' % calib_date.strftime("%d. %B %Y") )
days_since_calibration = dcco.days_since_calibration()
print('%d days since calibration' % days_since_calibration)
uid = dcco.uid()
print('DCC UID: %s' % uid)

if (days_since_calibration > 365):
    print('=> Recalibration required according to QMS.')

if dcco.is_signed():
    print('Signature available.')
    if dcco.is_signature_valid():
        print('Signature is valid.')
    else:
        print('Signature could not be verified.')
else:
    print('DCC is not signed.')

uncertainty_list = dcco.uncertainty_list()
for uncertainty in uncertainty_list:
    uncertainty_label = uncertainty[0]
    uncertainty_value = float(uncertainty[1])
    print("%s: %.8f" % (uncertainty_label, uncertainty_value) )
