# PyDCC
#
# Python module for processing of digital calibration certificates (DCC)
# according to https://www.ptb.de/dcc/
#
# Copyright (c) Siemens AG, 2022
#
# Authors:
#     Kai Mienert, PTB
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#

"""
This module downloads the DCC schemas provided by the Physikalisch-Technische Bundesanstalt.
All available versions are stored and made available by a function call.
Additionally the D-SI schemas are stored and also made available by a function call.
"""

import requests
# import urllib.request as urlib_requests
import json
import os
from typing import List, Dict
from xml.sax import make_parser, handler
import xmlschema
import xml.etree.ElementTree

# "url to load a json documents that hold information about the DCC versions"
url_dcc_schema_releases = "https://www.ptb.de/dcc/releases.json"

# the json document with dcc releases store uri's to download xsd files. These patterns are used to validate the uri's
mandatory_uri_pattern: List[str] = ["https", "ptb.de", "xsd"]


class DCCXMLValidator:

    def __init__(self, path_to_workspace: os.path = os.path.join(os.path.dirname(__file__), "schemas")):
        self.path_to_workspace = path_to_workspace

    def dcc_is_valid_against_schema(self, dcc_etree: xml.etree.ElementTree, dcc_version: str,
                                    online: bool = False) -> bool:
        """
        Validate DCC against the dcc schema

        :param dcc_etree: XML etree object build from dcc.xml
        :param dcc_version: version of teh dcc in case of online = False
        :param online: download referenced dcc schemas using location hints or use local stored xsd files
        :return: true if dcc is valid
        """
        is_valid: bool = False

        if online:
            is_valid = xmlschema.is_valid(xml_document=dcc_etree, use_location_hints=True)
        else:
            with open(self.get_abs_local_dcc_shema_path(dcc_version=dcc_version), 'r') as file:
                schema_file = file.read()

            locations = {"https://ptb.de/dcc": str(self.get_abs_local_dcc_shema_path(dcc_version=dcc_version)),
                         "https://ptb.de/si": str(self.get_abs_local_dsi_schema_path(dcc_version=dcc_version))}
            # TODO load all imports -> dcc 3.2.0
            if dcc_version == "3.2.0":
                locations["http://www.w3.org/2000/09/xmldsig#"] = str(
                    os.path.join(os.path.dirname(__file__), "schemas", "ds_0_1.xsd"))

            schema = xmlschema.XMLSchema(schema_file, build=True, allow="sandbox",
                                         base_url=os.path.join(os.path.dirname(__file__), "schemas"),
                                         locations=locations)

            is_valid = xmlschema.is_valid(xml_document=dcc_etree, schema=schema, use_location_hints=False)
        return is_valid

    def update_schemas(self, raise_errors: bool = False) -> bool:
        """
        Download all online available dcc schemas and make them available via get path functions.
        Based on the downloaded dcc schemas the required dsi schemas are downloaded.
        The dsi schemas are also available via corresponding get path function.

        :param raise_errors: Deactivates error messages and returns only False on failure
        :return: On success True is returned and on failure False
        """

        if not self.get_actual_list_ddc_xsd_releases_from_server(url=url_dcc_schema_releases,
                                                                 raise_errors=raise_errors):
            return False

        if "error" in self.download_dcc_schemas(raise_errors=raise_errors)[0]:
            return False

        if not self.download_dsi_shemas_referenced_by_downloaded_dcc_schemas(raise_errors=raise_errors):
            return False

        return True

    def get_dsi_info_from_dcc_schema(self, dcc_xsd_path: str, raise_errors: bool = False) -> dict:
        """
        Parses a dcc schemas and searches for the required dsi version

        :param dcc_xsd_path: path to dcc schemas
        :param raise_errors: Deactivates error messages and returns empty {} on failure
        :return: return version
        """

        parser = make_parser()
        dsi_version_handler = _HandlerDCCDSIVersion()
        parser.setContentHandler(dsi_version_handler)
        try:
            parser.parse(dcc_xsd_path)
        except _FinishedParsing:
            pass
        except Exception as e:
            if raise_errors:
                raise e
            return {}

        return {"version": dsi_version_handler.version, "schemaLocation": dsi_version_handler.schemaLocation}

    def get_dsi_info_from_dsi_schema(self, dsi_xsd_path: str, raise_errors: bool = False) -> str:
        """
        Parses a dsi schemas and searches for the required dsi version

        :param dsi_xsd_path: path to dsi schemas
        :param raise_errors: Deactivates error messages and returns "error" on failure
        :return: version of dsi schemas or "error"
        """

        parser = make_parser()
        dsi_version_handler = _HandlerDSIVersion()
        parser.setContentHandler(dsi_version_handler)
        try:
            parser.parse(dsi_xsd_path)
        except _FinishedParsing:
            pass
        except Exception as e:
            if raise_errors:
                raise e
            return "error"

        return dsi_version_handler.version

    def get_actual_list_ddc_xsd_releases_from_server(self, url: str, raise_errors: bool = True) -> bool:
        """
        Download a file with information and URI about the current schemas releases. The file will be saved in the
        Files folder.

        :param url: address for downloading the json file with the information about current releases.
        :param raise_errors: If False, error messages are suppressed and a False is returned.
        :return: On success True is returned and on failure False
        """

        """Download json document with releases"""
        try:
            data = requests.get(url, allow_redirects=True)
        except Exception as e:
            if raise_errors:
                raise e
            return False

        """Save downloaded file"""
        try:
            open(os.path.join(self.path_to_workspace, "dcc_releases.json"), 'wb').write(data.content)
        except Exception as e:
            if raise_errors:
                raise e
            return False

        return True

    def download_dcc_schemas(self, raise_errors: bool = False) -> List[str]:
        """
        Download all dcc schemas specified by the dcc_releases.json file with release type "stable"

        :param raise_errors: If False, error messages are suppressed and ["error"] is returned.
        :return: a list wih downloaded dcc schemas versions on success
        """

        try:
            with open(os.path.join(self.path_to_workspace, "dcc_releases.json")) as f_obj:
                release_list = json.load(f_obj).get("releases")
        except Exception as e:
            if raise_errors:
                raise e
            return ["error"]

        """prepare content template for creating dcc_version_info.json file"""
        dcc_version_info = {
            "description": "mapping dcc schemas versions to local dcc, dsi schemas files",
            "dcc_xsd_file": {},
            "dcc_dsi_match": {}
        }

        downloaded_schemas: List[str] = []

        for release in release_list:
            if release.get("type") == "stable":

                url = release.get("url")

                """validate schemaLocation URI with pattern"""
                for pattern in mandatory_uri_pattern:
                    if pattern not in url:
                        if raise_errors:
                            raise ValueError("one of the patterns was not found in the schemaLocation URI")
                        continue

                data = requests.get(url, allow_redirects=True)

                filename = "dcc_" + release.get("version").replace(".", "_") + ".xsd"

                dcc_version_info["dcc_xsd_file"][release.get("version")] = filename

                open(os.path.join(self.path_to_workspace, filename), 'wb').write(data.content)
                downloaded_schemas.append(filename)

        """store which dcc version was saved under which filename"""

        try:
            with open(os.path.join(self.path_to_workspace, "dcc_version_info.json"), "w") as outfile:
                json.dump(dcc_version_info, outfile, indent=4)
        except Exception as e:
            if raise_errors:
                raise e
            return ["error"]

        return downloaded_schemas

    def download_dsi_shemas_referenced_by_downloaded_dcc_schemas(self, raise_errors: bool = False) -> bool:
        """
        Based on the downloaded dcc schemas, the required dsi schemas are downloaded.
        The combination of dcc schemas version and dsi schemas file are saved for later use.

        :param raise_errors: If False, error messages are suppressed and a False is returned.
        :return: On success True is returned and on failure False
        """
        dcc_version_info = self.load_dcc_version_info_file_to_dict(raise_errors=raise_errors)

        if dcc_version_info == {}:
            if raise_errors:
                raise Exception('Can not load dcc version info')
            return False

        dcc_version_info["dcc_dsi_match"] = {}

        for key in dcc_version_info["dcc_xsd_file"]:

            path = os.path.join(self.path_to_workspace, dcc_version_info["dcc_xsd_file"][key])
            dsi_info = self.get_dsi_info_from_dcc_schema(path)

            if dsi_info == {}:
                continue

            """validate schemaLocation URI with pattern"""
            for pattern in mandatory_uri_pattern:
                if pattern not in dsi_info["schemaLocation"]:
                    # TODO Raise exception and set tag about download status in json file
                    print(dsi_info["schemaLocation"])
                    print("violate pattern")
                    continue

            """Try to download dsi document with releases"""
            try:
                print(dsi_info["schemaLocation"])
                data = requests.get(dsi_info["schemaLocation"], allow_redirects=True)
            except Exception as e:
                if raise_errors:
                    raise e
                continue

            """check if its really an xsd file or the download link was broken"""
            if "<?xml" not in data.text[:10]:
                print("no xml")
                continue

            """search dsi for version and compare it with the extracted version from dcc"""

            dsi_filename = "dsi_" + str(dsi_info["version"]).replace(".", "_") + ".xsd"

            dsi_filepath = os.path.join(self.path_to_workspace, dsi_filename)

            try:
                open(dsi_filepath, 'wb').write(data.content)
            except Exception as e:
                if raise_errors:
                    raise e
                return False

            version = self.get_dsi_info_from_dsi_schema(dsi_filepath)

            if version != str(dsi_info["version"]):
                if os.path.exists(dsi_filepath):
                    print(version)
                    print("wrong version")
                    os.remove(dsi_filepath)

            dcc_version_info["dcc_dsi_match"][key] = dsi_filename

            with open(os.path.join(self.path_to_workspace, "dcc_version_info.json"), "w") as outfile:
                json.dump(dcc_version_info, outfile, indent=4)

        return True

    def get_abs_local_dcc_shema_path(self, dcc_version: str = "3.1.1", raise_errors: bool = False) -> os.path:
        """
        Returns a path to an DCC xsd file corresponding to the given dcc version.
        If the version was not found locally None is returned.

        :param dcc_version: version dcc.xsd schemas for example "3.1.1"
        :param raise_errors: Deactivates error messages and returns only None on failure
        :return: absolute path to the local stored dcc.xsd file if search for version was succesfull
        """
        dcc_version_info = self.load_dcc_version_info_file_to_dict()

        try:
            filename = dcc_version_info["dcc_xsd_file"][dcc_version]
        except KeyError as e:
            if raise_errors:
                raise e
            return None

        return os.path.join(self.path_to_workspace, filename)

    def get_abs_local_dsi_schema_path(self, dcc_version: str = "3.1.1", raise_errors: bool = False) -> os.path:
        """
        Returns a path to an D-SI xsd file corresponding to the given dcc version.
        If the version was not found locally None is returned.

        :param dcc_version: version dcc.xsd schemas for example "3.1.1"
        :param raise_errors: Deactivates error messages and returns only None on failure
        :return: absolute path to the local stored dcc.xsd file if search for version was succesfull
        """
        dcc_version_info = self.load_dcc_version_info_file_to_dict()

        try:
            filename = dcc_version_info["dcc_dsi_match"][dcc_version]
        except KeyError as e:
            if raise_errors:
                raise e
            return None

        return os.path.join(self.path_to_workspace, filename)

    def load_dcc_version_info_file_to_dict(self, raise_errors: bool = False) -> Dict:
        """
        Loads the dcc_version_info file and returns it as python dictionary

        :param raise_errors: If False, error messages are suppressed and a False is returned.
        :return: dcc_version_info file as dictionary
        """
        try:
            with open(os.path.join(self.path_to_workspace, "dcc_version_info.json"), "r") as f_obj:
                dcc_version_info = json.load(f_obj)
        except Exception as e:
            if raise_errors:
                raise e
            return {}

        return dcc_version_info


class _FinishedParsing(Exception):
    """
    Error to stop parsing wit sax parser
    """
    pass


class _HandlerDCCDSIVersion(handler.ContentHandler):
    """
    Customized content handler for SAX perser and use with dcc schemas
    """

    def __init__(self):
        super().__init__()
        self.version: str = ""
        self.schemaLocation: str = ""

    def startElement(self, name, attrs):
        if "import" in name:
            if "si" in attrs["namespace"]:
                self.schemaLocation = attrs["schemaLocation"]
                temp = self.schemaLocation.split("/")
                for element in temp:
                    if len(element) > 0:
                        if element[0] == "v":
                            self.version = element[1:]
                raise _FinishedParsing


class _HandlerDSIVersion(handler.ContentHandler):
    """
    Customized content handler for SAX perser and use with dsi schemas
    """

    def __init__(self):
        super().__init__()
        self.version: str = ""

    def startElement(self, name, attrs):
        if "schema" in name:
            try:
                self.version = attrs["version"]
            except KeyError:
                raise _FinishedParsing
