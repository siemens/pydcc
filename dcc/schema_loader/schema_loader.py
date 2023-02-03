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

# set folder where files and schemas will be stored
files_folder = os.path.join(os.path.dirname(__file__), "..", "..", "data", "schemas")
# files_folder = os.path.join(os.path.dirname(__file__), "..", "schema")

# "url to load a json documents that hold informations about the DCC versions"
url_dcc_schema_releases = "https://www.ptb.de/dcc/releases.json"

# the json document with dcc releases store uri's to download xsd files. These patterns are used to validate the uri's
mandatory_uri_pattern: List[str] = ["https://www.ptb.de/", "xsd"]


def _load_dcc_version_info_file_to_dict(raise_errors: bool = False) -> Dict:
    """
    Loads the dcc_version_info file and returns it as python dictonary

    :param raise_errors: If False, error messages are suppressed and a False is returned.
    :return: dcc_version_info file as dictonary
    """
    try:
        with open(os.path.join(files_folder, "dcc_version_info.json"), "r") as f_obj:
            dcc_version_info = json.load(f_obj)
    except Exception as e:
        if raise_errors:
            raise e
        return {}

    return dcc_version_info


def _get_actual_list_ddc_xsd_releases_from_server(url: str, raise_errors: bool = True) -> bool:
    """
    Download a file with information and URI about the current schema releases. The file will be saved in the
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
        open(os.path.join(files_folder, "dcc_releases.json"), 'wb').write(data.content)
    except Exception as e:
        if raise_errors:
            raise e
        return False

    return True


def _download_dcc_schemas(raise_errors: bool = False) -> List[str]:
    """
    Download all dcc schemas specified by the dcc_releases.json file with release type "stable"

    :param raise_errors: If False, error messages are suppressed and ["error"] is returned.
    :return: a list wih downloaded dcc schema versions on success
    """

    try:
        with open(os.path.join(files_folder, "dcc_releases.json")) as f_obj:
            release_list = json.load(f_obj).get("releases")
    except Exception as e:
        if raise_errors:
            raise e
        return ["error"]

    """prepare content template for creating dcc_version_info.json file"""
    dcc_version_info = {
        "description": "mapping dcc schema versions to local dcc, dsi schema files",
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

            open(os.path.join(files_folder, filename), 'wb').write(data.content)
            downloaded_schemas.append(filename)

    """store which dcc version was saved under which filename"""

    try:
        with open(os.path.join(files_folder, "dcc_version_info.json"), "w") as outfile:
            json.dump(dcc_version_info, outfile, indent=4)
    except Exception as e:
        if raise_errors:
            raise e
        return ["error"]

    return downloaded_schemas


def _download_dsi_shemas_referenced_by_downloaded_dcc_schemas(raise_errors: bool = False) -> bool:
    """
    Based on the downloaded dcc schemas, the required dsi schemas are downloaded.
    The combination of dcc schema version and dsi schema file are saved for later use.

    :param raise_errors: If False, error messages are suppressed and a False is returned.
    :return: On success True is returned and on failure False
    """
    dcc_version_info = _load_dcc_version_info_file_to_dict(raise_errors=raise_errors)

    if dcc_version_info == {}:
        if raise_errors:
            raise Exception('Can not load dcc version info')
        return False

    dcc_version_info["dcc_dsi_match"] = {}

    for key in dcc_version_info["dcc_xsd_file"]:

        path = os.path.join(files_folder, dcc_version_info["dcc_xsd_file"][key])
        dsi_info = _get_dsi_info_from_dcc_schema(path)

        if dsi_info == {}:
            continue

        """validate schemaLocation URI with pattern"""
        for pattern in mandatory_uri_pattern:
            if pattern not in dsi_info["schemaLocation"]:
                continue

        """Try to download dsi document with releases"""
        try:
            data = requests.get(dsi_info["schemaLocation"], allow_redirects=True)
        except Exception as e:
            if raise_errors:
                raise e
            continue

        """check if its really an xsd file or the download link was broken"""
        if "<?xml" not in data.text[:10]:
            continue

        """search dsi for version and compare it with the extracted version from dcc"""

        dsi_filename = "dsi_" + str(dsi_info["version"]).replace(".", "_") + ".xsd"

        dsi_filepath = os.path.join(files_folder, dsi_filename)

        try:
            open(dsi_filepath, 'wb').write(data.content)
        except Exception as e:
            if raise_errors:
                raise e
            return False

        version = _get_dsi_info_from_dsi_schema(dsi_filepath)

        if version != str(dsi_info["version"]):
            if os.path.exists(dsi_filepath):
                os.remove(dsi_filepath)

        dcc_version_info["dcc_dsi_match"][key] = dsi_filename

        with open(os.path.join(files_folder, "dcc_version_info.json"), "w") as outfile:
            json.dump(dcc_version_info, outfile, indent=4)

    return True


def get_abs_local_dcc_shema_path(dcc_version: str = "3.1.1", raise_errors: bool = False) -> os.path:
    """
    Returns a path to an DCC xsd file corresponding to the given dcc version.
    If the version was not found locally None is returned.

    :param dcc_version: version dcc.xsd schema for example "3.1.1"
    :param raise_errors: Deactivates error messages and returns only None on failure
    :return: absolute path to the local stored dcc.xsd file if search for version was succesfull
    """
    dcc_version_info = _load_dcc_version_info_file_to_dict()

    try:
        filename = dcc_version_info["dcc_xsd_file"][dcc_version]
    except KeyError as e:
        if raise_errors:
            raise e
        return None

    return os.path.join(files_folder, filename)


def get_abs_local_dsi_shema_path(dcc_version: str = "3.1.1", raise_errors: bool = False) -> os.path:
    """
    Returns a path to an D-SI xsd file corresponding to the given dcc version.
    If the version was not found locally None is returned.

    :param dcc_version: version dcc.xsd schema for example "3.1.1"
    :param raise_errors: Deactivates error messages and returns only None on failure
    :return: absolute path to the local stored dcc.xsd file if search for version was succesfull
    """
    dcc_version_info = _load_dcc_version_info_file_to_dict()

    try:
        filename = dcc_version_info["dcc_dsi_match"][dcc_version]
    except KeyError as e:
        if raise_errors:
            raise e
        return None

    return os.path.join(files_folder, filename)


class _FinishedParsing(Exception):
    """
    Error to stop parsing wit sax parser
    """
    pass


class _HandlerDCCDSIVersion(handler.ContentHandler):
    """
    Customized content handler for SAX perser and use with dcc schema
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
    Customized content handler for SAX perser and use with dsi schema
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


def _get_dsi_info_from_dcc_schema(dcc_xsd_path: str, raise_errors: bool = False) -> dict:
    """
    Parses a dcc schema and searches for the required dsi version

    :param dcc_xsd_path: path to dcc schema
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


def _get_dsi_info_from_dsi_schema(dsi_xsd_path: str, raise_errors: bool = False) -> str:
    """
    Parses a dsi schema and searches for the required dsi version

    :param dsi_xsd_path: path to dsi schema
    :param raise_errors: Deactivates error messages and returns "error" on failure
    :return: version of dsi schema or "error"
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


def update_schemas(raise_errors: bool = False) -> bool:
    """
    Download all online available dcc schemas and make them available via get path functions.
    Based on the downloaded dcc schemas the required dsi schemas are downloaded.
    The dsi schemas are also available via corresponding get path function.

    :param raise_errors: Deactivates error messages and returns only False on failure
    :return: On success True is returned and on failure False
    """

    if not _get_actual_list_ddc_xsd_releases_from_server(url=url_dcc_schema_releases, raise_errors=raise_errors):
        return False

    if "error" in _download_dcc_schemas(raise_errors=raise_errors)[0]:
        return False

    if not _download_dsi_shemas_referenced_by_downloaded_dcc_schemas(raise_errors=raise_errors):
        return False

    return True
