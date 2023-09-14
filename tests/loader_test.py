# Unit tests for PyDCC
#
# Python module for processing of digital calibration certificates (DCC)
# according to https://www.ptb.de/dcc/
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#     Kai Mienert, PTB
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#
# SPDX-License-Identifier:  MIT
#

from dcc.dcc_xml_validator import DCCXMLValidator
from dcc.dcc_xml_validator import WORKSPACE_STATUS_OK
from dcc.dcc_xml_validator import get_imports_from_xml
from dcc.dcc_xml_validator import get_target_namespace_from_xml
from dcc.dcc_xml_validator import get_schema_version
import unittest
import xml.etree.ElementTree as ET
import os


class DxxXmlValidatorTest(unittest.TestCase):

    def test_workspcae_valid(self):
        val_obj = DCCXMLValidator(path_to_workspace="data/test_workspace")
        self.assertEqual(WORKSPACE_STATUS_OK, val_obj.workspace_status)
        self.cleanup_workspace("data/test_workspace")

    def test_get_imports_from_xml(self):
        with open("data/test.xsd", mode="r", encoding="utf-8") as file:
            xml_string = file.read()

        schema_locations = get_imports_from_xml(xml_string)
        self.assertEqual(schema_locations, ['schemaLocation1', 'schemaLocation2'])

    def test_get_target_namespace_from_xml(self):
        with open("data/test.xsd", mode="r", encoding="utf-8") as file:
            xml_string = file.read()

        target_namespace = get_target_namespace_from_xml(xml_string)
        self.assertEqual(target_namespace, "namespace1")

    def test_get_schema_version(self):
        with open("../data/dcc/dcc_gp_temperatur_resistance_v12.xml", mode="r", encoding="utf-8") as file:
            xml_string = file.read()

        schema_version = get_schema_version(xml_string)
        self.assertEqual(schema_version, "3.1.1")

    def test_online_schema_validation(self):
        val_obj = DCCXMLValidator(workspace_init=False)
        with self.subTest():
            dcc_tree = ET.parse("../data/dcc/dcc_gp_humidity_v1.0.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.2", online=True)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("../data/dcc/dcc_gp_temperatur_resistance_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=True)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("../data/dcc/dcc_gp_temperature_extensive_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=True)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("../data/dcc/dcc_gp_temperature_simplified_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=True)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("../data/dcc/dcc_gp_temperature_typical_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=True)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("../data/dcc/dcc_gp_temperature_typical_adjustment_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=True)
            self.assertEqual(valid, True)

    def test_offline_schema_validation(self):
        val_obj = DCCXMLValidator()
        with self.subTest():
            dcc_tree = ET.parse("../data/dcc/dcc_gp_humidity_v1.0.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.2", online=False)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("../data/dcc/dcc_gp_temperatur_resistance_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=False)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("../data/dcc/dcc_gp_temperature_extensive_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=False)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("../data/dcc/dcc_gp_temperature_simplified_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=False)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("../data/dcc/dcc_gp_temperature_typical_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=False)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("../data/dcc/dcc_gp_temperature_typical_adjustment_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=False)
            self.assertEqual(valid, True)

        self.cleanup_workspace("data/test_workspace")

    def cleanup_workspace(self, workspace):
        for f in os.listdir(workspace):
            if "Readme.md" in f:
                continue
            os.remove(os.path.join(workspace, f))


if __name__ == "__main__":
    unittest.main()
