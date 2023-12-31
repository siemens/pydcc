# PyDCC
#
# Python module for processing of digital calibration certificates (DCC)
# according to https://www.ptb.de/dcc/
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

xml_file_name = '../data/dcc/dcc_gp_temperature_typical_v12.xml' # Example from PTB
dcco = DCC(xml_file_name) # Load DCC and crate DCC object

if not dcco.status_report.is_loaded:
    print("Error: DCC was not loaded successfully!")

dcco.verify_dcc_xml(online=True)

if dcco.status_report.schema_verification_performed:
    if dcco.status_report.valid_schema:
        print("XML schema is valid.")
    else:
        print("Error: XML schema is invalid.")
else:
    print("Warning: XML schema verification was not performed!")

calib_date = dcco.calibration_date()
print('Calibration date: %s' % calib_date.strftime("%d. %B %Y") )
days_since_calibration = dcco.days_since_calibration()
print('%d days since calibration' % days_since_calibration)
uid = dcco.uid()
print('DCC UID: %s' % uid)

calibration_cycle_in_days = 365
if (days_since_calibration > calibration_cycle_in_days):
    print('Recalibration overdue according to QMS.')
else:
    next_calibration_in_days = calibration_cycle_in_days - days_since_calibration
    print('Next recalibration in %u days according to QMS.' % next_calibration_in_days)

if dcco.status_report.is_signed:
    print('Signature available.')
    if dcco.status_report.valid_signature:
        print('Signature is valid.')
    else:
        print('Error: Signature could not be verified.')
else:
    print('Warning: DCC is not signed.')


status_summary_flag = dcco.status_report.get_status_summary()
if (status_summary_flag):
    print('All test were passed.')
else:
    print('Warning: Some test failed.')
    print(dcco.status_report)