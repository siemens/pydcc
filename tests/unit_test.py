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
# This work is licensed under the terms of the MIT License. 
# See the LICENSE file in the top-level directory.
#
import sys

sys.path.append("../src/")
from dcc import dcc
import datetime
import unittest

xml_file_name = 'DCC_3_GrundstrukturPyDCC.xml'
xml_file_path = '../data/dcc/' + xml_file_name
dcco = dcc(xml_file_path)


class TestBaseFunctions(unittest.TestCase):

    def test_loading_from_file(self):
        dcc_from_file = dcc(xml_file_path)  # Load DCC and crate DCC object
        self.assertTrue(dcc_from_file.is_loaded())

    def test_loading_byte_array(self):
        with open(xml_file_path, "rb") as f:
            dcc_byte_array = f.read()
        dcc_from_byte_array = dcc(byte_array=dcc_byte_array)  # Load DCC and crate DCC object
        self.assertTrue(dcc_from_byte_array.is_loaded())

    def test_loading_compressed_byte_array(self):
        compressed_file = xml_file_name.split('.')
        with open("../data/compressed_dcc/" + compressed_file[0] + ".pydcc", "rb") as f:
            dcc_compressed = f.read()
        dcc_from_compresed_byte_array = dcc(compressed_dcc=dcc_compressed)  # Load DCC and crate DCC object
        self.assertTrue(dcc_from_compresed_byte_array.is_loaded())

    def test_calibration_date(self):
        calib_date = dcco.calibration_date()
        ref_date = datetime.datetime(2021, 10, 27, 0, 0)
        self.assertEqual(calib_date, ref_date)

    def test_days_since_calibration(self):
        days = dcco.days_since_calibration()
        self.assertTrue(days > 40)

    def test_uid(self):
        uid = dcco.uid()
        self.assertEqual(uid, "XXXXXXXXXXXX")

    def test_version(self):
        version = dcco.version()
        self.assertEqual(version, "3.0.0")

    def test_uncertainty_list(self):
        uncertainty_list = dcco.uncertainty_list()
        self.assertEqual(uncertainty_list, [['Masse', '0.00000005'], ['Volumen', '0.000018']])

    def test_empty_dcc_init_error_detection(self):
        exception_rised = False
        try:
            dcc_empty = dcc()
        except Exception:
            exception_rised = True
        self.assertTrue(exception_rised)

    def test_is_not_signed(self):
        self.assertFalse(dcco.is_signed())

    def test_is_signed(self):
        xml_file_name = '../data/dcc/signed_siliziumkugel.xml'  # Example from PTB and signed by T-Systems
        dcc_signed = dcc(xml_file_name)
        self.assertTrue(dcc_signed.is_signed())

    def test_compressed_dcc_crc(self):
        comp_dcc = dcco.generate_compressed_dcc()
        crc32 = comp_dcc['crc32']
        self.assertEqual(crc32, 251633089)

    def test_compressed_dcc_size(self):
        comp_dcc = dcco.generate_compressed_dcc()
        bytes_compressed = comp_dcc['bytes_compressed']
        self.assertEqual(bytes_compressed, 7826)

    def test_previous_report_not_available(self):
        self.assertFalse(dcco.has_previous_report())


#    def test_verify_correct_dcc_xml(self):
#        self.assertTrue(dcco.verify_dcc_xml())

#    def test_verify_incorrect_dcc_xml(self):
#        xml_file_name_wrong_schema = '../data/siliziumkugel_wrong_schema.xml' # Example from PTB
#        dcco_wrong_schema = dcc(xml_file_name_wrong_schema)        
#        self.assertFalse(dcco_wrong_schema.verify_dcc_xml())

# Work in progress

# def test_is_signature_valid(self):
#    self.assertFalse(dcco.is_signature_valid())


if __name__ == '__main__':
    unittest.main()
