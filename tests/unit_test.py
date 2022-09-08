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

xml_file_name_gp = 'dcc_gp_temperature_typical_v12.xml'
xml_file_path_gp = '../data/dcc/' + xml_file_name_gp
dcco_gp = DCC(xml_file_path_gp)


class TestBaseFunctions(unittest.TestCase):

    def test_loading_from_file(self):
        dcc_from_file = DCC(xml_file_path_gp)  # Load DCC and crate DCC object
        self.assertTrue(dcc_from_file.is_loaded())

    def test_loading_byte_array(self):
        with open(xml_file_path_gp, "rb") as f:
            dcc_byte_array = f.read()
        dcc_from_byte_array = DCC(byte_array=dcc_byte_array)  # Load DCC and crate DCC object
        self.assertTrue(dcc_from_byte_array.is_loaded())

    def test_loading_compressed_byte_array(self):
        compressed_file = xml_file_name_gp.split('.')
        with open("../data/compressed_dcc/" + compressed_file[0] + ".pydcc", "rb") as f:
            dcc_compressed = f.read()

        dcc_from_compressed_byte_array = DCC(compressed_dcc=dcc_compressed)  # Load DCC and crate DCC object
        self.assertTrue(dcc_from_compressed_byte_array.is_loaded())

    def test_mandatoryLang(self):
        lang = dcco_gp.mandatoryLang()
        self.assertEqual(lang, 'de')

    def test_get_calibration_result_by_quantity_id(self):
        dcco = DCC('../data/dcc/dcc_ngp_temperature_typical_v12_refType2ID.xml')
        res = dcco.get_calibration_result_by_quantity_id('basic_measurementError')
        self.assertEqual(res, ['0.072 0.089 0.107 -0.009 -0.084', '\\kelvin', 'expandedUncXMLList->uncertaintyXMLList', '0.061', ' k:', '2'])

    def test_get_calibration_results(self):
        res = dcco_gp.get_calibration_results()
        self.assertEqual(res[0], ['  Messergebnisse  Bezugswert', [['306.248 373.121 448.253 523.319 593.154', '\\kelvin'], ['33.098 99.971 175.103 250.169 320.004', '\\degreecelsius']]])
        self.assertEqual(res[1], ['  Messergebnisse  Angezeigter Messwert Kalibriergegenstand', [['306.32 373.21 448.36 523.31 593.07', '\\kelvin'], ['33.17 100.06 175.21 250.16 319.92', '\\degreecelsius']]])
        self.assertEqual(res[2], ['  Messergebnisse  Messabweichung', ['0.072 0.089 0.107 -0.009 -0.084', '\\kelvin', 'expandedUncXMLList->uncertaintyXMLList', '0.061', ' k:', '2']])

    def test_calibration_date(self):
        calib_date = dcco_gp.calibration_date()
        ref_date = datetime.datetime(1957, 8, 13, 0, 0)
        self.assertEqual(calib_date, ref_date)

    def test_days_since_calibration(self):
        days = dcco_gp.days_since_calibration()
        self.assertTrue(days > 40)

    def test_calibration_laboratory_name(self):
        calib_lab_name = dcco_gp.calibration_laboratory_name()
        ref_lab_name = 'Kalibrierfirma GmbH'
        self.assertEqual(calib_lab_name, ref_lab_name)

    def test_uid(self):
        uid = dcco_gp.uid()
        self.assertEqual(uid, "GP_DCC_temperature_typical_1.2")

    def test_version(self):
        version = dcco_gp.version()
        self.assertEqual(version, "3.1.1")

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
        self.assertFalse(dcco_gp.is_signed())

    def test_is_signed(self):
        xml_file_name = '../data/dcc/signed_siliziumkugel.xml'  # Example from PTB and signed by T-Systems
        dcc_signed = DCC(xml_file_name)
        self.assertTrue(dcc_signed.is_signed())

    def test_compressed_dcc_crc(self):
        comp_dcc = dcco_gp.generate_compressed_dcc()
        crc32 = comp_dcc['crc32']
        self.assertEqual(crc32, 2189713291)

    def test_compressed_dcc_size(self):
        comp_dcc = dcco_gp.generate_compressed_dcc()
        bytes_compressed = comp_dcc['bytes_compressed']
        self.assertEqual(bytes_compressed, 4480)

    def test_previous_report_available(self):
        self.assertFalse(dcco_gp.has_previous_report())

    def test_item_id(self):
        id_dict_v3 = {'identifications': {'identification': [{'issuer': 'manufacturer', 'value': 'string-manufacturer-item',
                                                 'name': {'content': [{'@lang': 'de', '#text': 'Serien Nr.'},
                                                                      {'@lang': 'en', '#text': 'Serial no.'}]}},
                                                {'issuer': 'customer', 'value': 'string-customer-item', 'name': {
                                                    'content': [{'@lang': 'de', '#text': 'Messmittel Nr.'},
                                                                {'@lang': 'en',
                                                                 '#text': 'Measurement equipment no.'}]}},
                                                {'issuer': 'calibrationLaboratory',
                                                 'value': 'string-calibrationLaboratory-item', 'name': {
                                                    'content': [{'@lang': 'de', '#text': 'Equipment Nr.'},
                                                                {'@lang': 'en', '#text': 'Equipment no.'}]}}]}}

        self.assertEqual(dcco_gp.item_id(), id_dict_v3)

    def test_verify_correct_dcc_xml(self):
        self.assertTrue(dcco_gp.verify_dcc_xml())

    def test_verify_incorrect_dcc_xml(self):
        xml_file_name_wrong_schema = '../data/siliziumkugel_wrong_schema.xml' # Example from PTB
        dcco_wrong_schema = DCC(xml_file_name_wrong_schema)
        self.assertFalse(dcco_wrong_schema.verify_dcc_xml())

# Work in progress

# def test_is_signature_valid(self):
#    self.assertFalse(dcco.is_signature_valid())


if __name__ == '__main__':
    unittest.main()
