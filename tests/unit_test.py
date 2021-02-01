# Unit tests for PyDCC
# 
# This software was licensed under Apache 2.0 
# https://www.apache.org/licenses/LICENSE-2.0
#
import unittest
import sys
sys.path.append("../src/")
import dcc
import datetime

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


