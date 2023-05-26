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
from typing import List, Dict, Optional, Callable
import platform
from xml.sax import make_parser, handler
import xmlschema
import xml.etree.ElementTree as ET
from pydantic import BaseModel
from datetime import datetime

# "url to load a json documents that hold information about the DCC versions"
url_dcc_schema_releases = "https://www.ptb.de/dcc/releases.json"

# the json document with dcc releases store uri's to download xsd files. These patterns are used to validate the uri's
mandatory_uri_pattern: List[str] = ["https", "ptb.de", "xsd"]


def standard_workspace(get_system: Optional[Callable] = platform.system) -> os.path:
    # Get the system the programm is running on to decide what folder should be used
    if get_system is None:
        get_system = platform.system

    system = get_system()
    if system == "Windows":
        appdata_path = os.getenv('APPDATA')
    elif system == "Linux":
        appdata_path = os.path.expanduser('~')
    elif system == "Darwin":
        appdata_path = os.path.expanduser('~/Library/Application Support')
    else:
        return None

    folder_path = os.path.join(appdata_path, 'pydcc')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Create a Readme.txt file inside the Folder with some information about the usage.

    readme_content = "This directory was created by the pyDCC software.\nIt is used to store downloaded xml schemas." \
                     "\nThese are used for the validation of the DCCs." + "\n\n" + "Created on: " + str(datetime.now())

    file_path = os.path.join(folder_path, 'Readme.txt')
    if not os.path.exists(file_path):
        with open(file_path, mode="w") as file:
            file.write(readme_content)

    return folder_path


class Dependency(BaseModel):
    # imported schemas by dcc schema
    online_schemaLocation: str = ""
    namespace: str = ""


class Schema(BaseModel):
    # Data to describe the schema
    targetNamespace: str = ""
    filename: str = ""
    version_str: str = ""
    version_int: str = ""
    location_local_abs: str = ""
    online_schemaLocation: str = ""

    # dependencies
    dependencys: List[Dependency] = []


class DCCRelease(BaseModel):
    """
    used subelement to parse json file from  https://www.ptb.de/dcc/releases.json
    """
    version: str = ""
    url: str = ""
    type: str = ""


class DCCOnlineReleases(BaseModel):
    """
    parse json file from  https://www.ptb.de/dcc/releases.json
    """
    description: str = ""
    releases: List[DCCRelease] = DCCRelease()


class Data(BaseModel):
    """
    store information about downloaded schemas
    """
    online_available_releases: DCCOnlineReleases = DCCOnlineReleases()
    local_available_schemas: List[Schema] = []
    last_update: datetime = datetime.now()


class DCCXMLValidator:

    def __init__(self, path_to_workspace: Optional[str] = None, init_local_schemas: bool = True):

        #  set workspace where schemas will be stored locally on the machine. Used to perform offline schema validation
        if path_to_workspace is None:
            self.path_workspace = standard_workspace()
        else:
            self.path_workspace = path_to_workspace


        self.path_data_file = os.path.join(self.path_workspace, "schemas.json")

        # check if workspace is valid
        # self.workspace_valid = self.workspace_is_valid()
        self.data = Data()


    def workspace_is_valid(self) -> bool:

        try:
            with open(self.path_workspace, mode="r") as file:
                datax = json.load(file)
        except Exception as e:
            print(e)
            return False

        try:
            self.data = Data(**datax)
        except Exception as e:
            print(e)
            return False

        # TODO

        return True

    def dcc_is_valid_against_schema(self, dcc_etree: ET, dcc_version: str,
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

    def download_list_with_avalable_releases(self, raise_errors: bool = True) -> bool:
        """
        Download a list with all available dcc schemas

        :param raise_errors: Deactivates error messages and returns only False on failure
        :return: On success True is returned and on failure False
        """

        """Download json document with releases"""
        try:
            download = requests.get(url_dcc_schema_releases, allow_redirects=True)
        except Exception as e:
            if raise_errors:
                raise e
            return False

        """Parse data"""
        datax = download.json()
        self.data.online_available_releases = DCCOnlineReleases(**datax)

        for release in self.data.online_available_releases.releases:

            # onely download stable releases
            if release.type != "stable":
                continue

        with open(self.path_data_file, mode="w") as file:
            file.write(self.data.json(indent=4))

    def download_schemas(self):

        self.load_data_file_from_workspace()

        for release in self.data.online_available_releases.releases:
            try:
                download = requests.get(release.url, allow_redirects=True)
            except Exception as e:
                print(e)
                continue

            if release.type != "stable":
                continue

            # save downloaded xsd schema content to file
            filename = "dcc_" + release.version.replace(".", "_") + ".xsd"
            with open(os.path.join(self.path_workspace, filename), mode="wb") as file:
                file.write(download.content)

            schema = Schema(targetNamespace=self.get_target_namespace_from_xml((download.content.decode("utf-8"))),
                            filename=filename,
                            version_str=release.version.replace(".", "_"),
                            version_int=int(release.version.replace(".", "")),
                            location_local_abs=str(os.path.join(self.path_workspace, filename)),
                            online_schemaLocation=release.url,
                            dependencys=self.get_imports_from_xml((download.content.decode("utf-8"))))
            self.data.local_available_schemas.append(schema)

        self.save_data_file_to_workspace()

    def get_imports_from_xml(self, xml_string: str):

        root = ET.fromstring(xml_string)

        # Find all elements with the tag "import"
        import_elements = root.findall(".//{*}import")
        dependencys = []

        # Iterate over each import element
        for element in import_elements:

            if "schemaLocation" in element.attrib:
                tmp = Dependency(online_schemaLocation=element.attrib["schemaLocation"],
                                        namespace=element.attrib["namespace"])

                dependencys.append(tmp)

        return dependencys

    def download_dependencys(self):

        self.load_data_file_from_workspace()

        downloaded_schemas = []

        for entry in self.data.local_available_schemas:
            for dependecny in entry.dependencys:
                try:
                    download = requests.get(dependecny.online_schemaLocation, allow_redirects=True)
                except Exception as e:
                    print(e)
                    continue
                # save downloaded xsd schema content to file
                if "<?xml" not in download.content.decode("utf-8")[0:10]:
                    continue

                target_namespace = self.get_target_namespace_from_xml(download.content.decode("utf-8"))
                version = self.get_version_from_xml(download.content.decode("utf-8"))

                filename = target_namespace.split("/")[-1] + "_" + version.replace(".", "_") + ".xsd"
                with open(os.path.join(self.path_workspace, filename), mode="wb") as file:
                    file.write(download.content)

                new_schema = Schema(targetNamespace=target_namespace,
                       filename=filename,
                       version_str=version.replace(".", "_"),
                       version_int=int(version.replace(".", "")),
                       location_local_abs=str(os.path.join(self.path_workspace, filename)),
                       online_schemaLocation=dependecny.online_schemaLocation,
                       dependencys=self.get_imports_from_xml((download.content.decode("utf-8"))))

                for schema in self.data.local_available_schemas:
                    if schema.online_schemaLocation == new_schema.online_schemaLocation:
                        continue

                downloaded_schemas.append(new_schema)

        for schema in downloaded_schemas:
            self.data.local_available_schemas.append(schema)

        self.save_data_file_to_workspace()

    def save_data_file_to_workspace(self):

        self.data.last_update = str(datetime.now())

        with open(self.path_data_file, mode="w") as file:
            file.write(self.data.json(indent=4))

    def load_data_file_from_workspace(self):

        with open(self.path_data_file, mode="r", encoding="utf-8") as file:
            self.data = Data(**json.load(file))

    def get_target_namespace_from_xml(self, xml_string: str):

        root = ET.fromstring(xml_string)
        if "targetNamespace" in root.attrib:
            return root.attrib.get("targetNamespace")
        return ""
    def get_version_from_xml(self, xml_string: str):

        root = ET.fromstring(xml_string)
        return root.attrib.get("version")




