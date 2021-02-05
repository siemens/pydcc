# Unit tests for PyDCC
#
# Python module for processing of digital calibration certificates (DCC)
# according to https://www.ptb.de/dcc/
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Andreas Tobola <andreas.tobola@siemens.com>
#
# This work is licensed under the terms of the MIT license. 
# See the LICENSE file in the top-level directory.
#
import sys
sys.path.append("../src/")
import dcc
import datetime
import unittest

xml_file_name = '../data/siliziumkugel.xml' # Example from PTB
dcco = dcc.dcc(xml_file_name)

class TestBaseFunctions(unittest.TestCase):

    def test_loading_from_file(self):
        #dcco = dcc.dcc(xml_file_name) # Load DCC and crate DCC object
        self.assertTrue(dcco.is_loaded())

    def test_verify_dcc_xml_file(self):
        self.assertFalse(dcco.verify_dcc_xml_file())
        
    def test_is_signed(self):
        self.assertFalse(dcco.is_signed())

    def test_is_signature_valid(self):
        self.assertFalse(dcco.is_signature_valid())

    def test_calibration_date(self):
        calib_date = dcco.calibration_date()        
        ref_date = datetime.datetime(2018, 10, 12, 0, 0)
        self.assertEqual(calib_date, ref_date)

    def test_days_since_calibration(self):
        days = dcco.days_since_calibration()
        self.assertTrue(days > 842)

if __name__ == '__main__':
    unittest.main()


