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
from dcc import DCC
import datetime
import unittest

xml_file_name = 'DCC_3_GrundstrukturPyDCC.xml'
xml_file_path = '../data/dcc/' + xml_file_name
dcco = DCC(xml_file_path)


class TestBaseFunctions(unittest.TestCase):

    def test_loading_from_file(self):
        dcc_from_file = DCC(xml_file_path) # Load DCC and crate DCC object
        self.assertTrue(dcc_from_file.is_loaded())

    def test_loading_byte_array(self):
        with open(xml_file_path, "rb") as f:
            dcc_byte_array = f.read()
        dcc_from_byte_array = DCC(byte_array = dcc_byte_array) # Load DCC and crate DCC object
        self.assertTrue(dcc_from_byte_array.is_loaded())

    def test_loading_compressed_byte_array(self):
        compressed_file = xml_file_name.split('.')
        with open("../data/compressed_dcc/" + compressed_file[0] + ".pydcc", "rb") as f:
            dcc_compressed = f.read()
        dcc_from_compresed_byte_array = DCC(compressed_dcc = dcc_compressed) # Load DCC and crate DCC object
        self.assertTrue(dcc_from_compresed_byte_array.is_loaded())

    def test_mandatoryLang(self):
        lang = dcco.mandatoryLang()
        self.assertEqual(lang, 'de')

    def test_get_calibration_result_by_quantity_id(self):
        dccno = DCC('../data/Uncertainty2_PyDCC.xml')
        res = dccno.get_calibration_result_by_quantity_id('MeasRes1_res1_quant1')
        self.assertEqual(res, ['11111', '\\milli\\metre', ' expanded uncertainty:', '0.11111', ' k:', '2.0'])

    def test_get_calibration_results(self):
        dccno = DCC('../data/Uncertainty2_PyDCC.xml')
        res = dccno.get_calibration_results()
        self.assertEqual(res[0], ['  MEAS_RES1_res1', ['11111', '\\milli\\metre', ' expanded uncertainty:', '0.11111', ' k:', '2.0']])
        self.assertEqual(res[1], ['  MEAS_RES1_res1', ['22222', '\\milli\\metre', ' expanded uncertainty:', '0.22222', ' k:', '2.0']])

    def test_calibration_date(self):
        calib_date = dcco.calibration_date()
        ref_date = datetime.datetime(2021, 10, 27, 0, 0)
        self.assertEqual(calib_date, ref_date)

    def test_days_since_calibration(self):
        days = dcco.days_since_calibration()
        self.assertTrue(days > 40)

    def test_calibration_laboratory_name(self):
        calib_lab_name = dcco.calibration_laboratory_name()        
        ref_lab_name = 'Kalibrierlab XXXXXXXXX'
        self.assertEqual(calib_lab_name, ref_lab_name)       

    def test_uid(self):
        uid = dcco.uid()
        self.assertEqual(uid, "XXXXXXXXXXXX")

    def test_version(self):
        version = dcco.version()
        self.assertEqual(version, "3.0.0")


    """
    def test_uncertainty_list(self):
        uncertainty_list = dcco.uncertainty_list()
        self.assertEqual(uncertainty_list, [['Masse', '0.00000005'], ['Volumen', '0.000018']])
       
    """
 

    def test_empty_dcc_init_error_detection(self):
        exception_rised = False
        try:
            dcc_empty = DCC()
        except Exception:
            exception_rised = True
        self.assertTrue(exception_rised)

    def test_is_not_signed(self):
        self.assertFalse(dcco.is_signed())

    def test_is_signed(self):
        xml_file_name = '../data/dcc/signed_siliziumkugel.xml'  # Example from PTB and signed by T-Systems
        dcc_signed = DCC(xml_file_name)
        self.assertTrue(dcc_signed.is_signed())

    def test_compressed_dcc_crc(self):
        comp_dcc = dcco.generate_compressed_dcc()
        crc32 = comp_dcc['crc32']
        self.assertEqual(crc32, 251633089)

    def test_compressed_dcc_size(self):
        comp_dcc = dcco.generate_compressed_dcc()
        bytes_compressed = comp_dcc['bytes_compressed']
        self.assertEqual(bytes_compressed, 7826)

    def test_previous_report_available(self):
        self.assertTrue(dcco.has_previous_report())

    def test_item_id(self):
        id_dict_v2 = {'issuer': 'manufacturer', 'value': 'Si28kg_03_a', 'content (lang: de)': 'Kennnummer',
                      'content (lang: en)': 'Serial No.'}

        id_dict_v3 = {'issuer': 'manufacturer', 'value': 'itemManufacturer',
                      'content (lang: de)': 'Fabrikat/Serien-Nr.', 'content (lang: en)': 'Serial number'}

        if dcco.version() == '2.4.0':
            self.assertEqual(dcco.item_id(), id_dict_v2)
        elif dcco.version() == '3.0.0':
            self.assertEqual(dcco.item_id(), id_dict_v3)



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


