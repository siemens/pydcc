import dcc.dcc_xml_validator as validator
import unittest
import xml.etree.ElementTree as ET
import os


class DxxXmlValidatorTest(unittest.TestCase):

    def test_workspcae_valid(self):
        val_obj = validator.DCCXMLValidator(path_to_workspace="data/test_workspace", workspace_init=True)
        self.assertEqual(validator.WORKSPACE_STATUS_OK, val_obj.workspace_status)
        self.cleanup_workspace("data/test_workspace")

    def _test_workspace_broken(self):
        with self.subTest():
            val_obj = validator.DCCXMLValidator(path_to_workspace="data/test_workspace", workspace_init=False)
            self.assertEqual(val_obj.workspace_status, validator.WORKSPACE_STATUS_JSON_FILE_CORRUPTED)
        with self.subTest():
            val_obj = validator.DCCXMLValidator(path_to_workspace="data/test_workspace", workspace_init=False)
            self.assertEqual(val_obj.workspace_status, validator.WORKSPACE_STATUS_MISSING_SCHEMA_FILES)
        with self.subTest():
            val_obj = validator.DCCXMLValidator(path_to_workspace="data/test_workspace", workspace_init=False)
            self.assertEqual(val_obj.workspace_status, validator.WORKSPACE_STATUS_NO_DATA_FILE)
        with self.subTest():
            val_obj = validator.DCCXMLValidator(path_to_workspace="data/test_workspace", workspace_init=False)
            self.assertEqual(val_obj.workspace_status, validator.WORKSPACE_NO_README)
        with self.subTest():
            val_obj = validator.DCCXMLValidator(path_to_workspace="data/test_workspace", workspace_init=False)
            self.assertEqual(val_obj.workspace_status, validator.WORKSPACE_PATH_DOES_NOT_EXIST)

    def test_get_imports_from_xml(self):
        with open("data/test.xsd", mode="r", encoding="utf-8") as file:
            xml_string = file.read()

        schema_locations = validator.get_imports_from_xml(xml_string)
        self.assertEqual(schema_locations, ['schemaLocation1', 'schemaLocation2'])

    def test_get_target_namespace_from_xml(self):
        with open("data/test.xsd", mode="r", encoding="utf-8") as file:
            xml_string = file.read()

        target_namespace = validator.get_target_namespace_from_xml(xml_string)
        self.assertEqual(target_namespace, "namespace1")

    def test_get_schema_version(self):
        with open("data/dcc_gp_temperatur_resistance_v12.xml", mode="r", encoding="utf-8") as file:
            xml_string = file.read()

        schema_version = validator.get_schema_version(xml_string)
        self.assertEqual(schema_version, "3.1.1")

    def test_oneline_schema_validation(self):
        # TODO generate workspaces for testing
        val_obj = validator.DCCXMLValidator(workspace_init=False)
        with self.subTest():
            dcc_tree = ET.parse("data/dcc_gp_humidity_v1.0.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.2", online=True)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("data/dcc_gp_temperatur_resistance_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=True)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("data/dcc_gp_temperature_extensive_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=True)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("data/dcc_gp_temperature_simplified_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=True)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("data/dcc_gp_temperature_typical_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=True)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("data/dcc_gp_temperature_typical_adjustment_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=True)
            self.assertEqual(valid, True)

    def test_offline_schema_validation(self):
        val_obj = validator.DCCXMLValidator(workspace_init=True)
        with self.subTest():
            dcc_tree = ET.parse("data/dcc_gp_humidity_v1.0.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.2", online=False)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("data/dcc_gp_temperatur_resistance_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=False)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("data/dcc_gp_temperature_extensive_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=False)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("data/dcc_gp_temperature_simplified_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=False)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("data/dcc_gp_temperature_typical_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=False)
            self.assertEqual(valid, True)
        with self.subTest():
            dcc_tree = ET.parse("data/dcc_gp_temperature_typical_adjustment_v12.xml")
            valid = val_obj.dcc_is_valid_against_schema(dcc_etree=dcc_tree, dcc_version="3.1.1", online=False)
            self.assertEqual(valid, True)

        self.cleanup_workspace("data/test_workspace")

    def cleanup_workspace(self, workspace):
        for f in os.listdir(workspace):
            os.remove(os.path.join(workspace, f))


if __name__ == "__main__":
    unittest.main()
