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
This module can be used to validate a Digital Calibration Certificate (DCC). The DCCXMLValidator class is used to
perform the validation. The Physikalisch-Technische Bundesanstalt provides a Json document. This document lists
all current DCC schemas. The class DCCXMLValidator downloads all schemas listed in the json file. For validation
the function dcc_is_valid_against_schema can be used. The user specifies whether the previously downloaded schemas
are used or the schemaLocations in the DCC-xml file are used.

The DCC schemas and all other dependencies are stored in a workspace. This is usually located in a specified folder.
However, the user can define the workspace himself. For licensing reasons, the schemas cannot be stored in the
project/module directory.
"""

import requests
import json
import os
from typing import List, Optional, Callable
import platform
import xmlschema
import xml.etree.ElementTree as ET
from pydantic import BaseModel, ValidationError
from datetime import datetime

# "url to load a json documents that hold information about the DCC versions"
url_dcc_schema_releases = "https://www.ptb.de/dcc/releases.json"


class DccXmlValidator(Exception):
    """General exception."""


class DccSchemaNotAvailableLocal(DccXmlValidator):
    """No locally available schema was found for the DCC to be validated."""


def get_standard_workspace_path() -> os.path:
    # Get the system the programm is running on to decide what folder should be used

    system = platform.system()
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

    return folder_path


def get_imports_from_xml(xml_string: str):
    root = ET.fromstring(xml_string)

    # Find all elements with the tag "import"
    import_elements = root.findall(".//{*}import")
    dependencys: List[str] = []

    # Iterate over each import element
    for element in import_elements:
        if "schemaLocation" in element.attrib:
            dependencys.append(element.attrib["schemaLocation"])

    return dependencys


def get_target_namespace_from_xml(xml_string: str):
    root = ET.fromstring(xml_string)
    if "targetNamespace" in root.attrib:
        return root.attrib.get("targetNamespace")
    return ""


def get_schema_version(xml_string: str):
    root = ET.fromstring(xml_string)
    if "schemaVersion" in root.attrib:
        return root.attrib.get("schemaVersion")
    if "version" in root.attrib:
        return root.attrib.get("version")
    return ""


class Schema(BaseModel):
    # Data to describe the schema
    targetNamespace: str = ""
    filename: str = ""
    version_str: str = ""
    location_local_abs: str = ""
    online_schemaLocation: str = ""

    # dependencies
    dependencys: List[str] = []


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


WORKSPACE_STATUS_OK = 0
WORKSPACE_PATH_DOES_NOT_EXIST = 1
WORKSPACE_NO_README = 2
WORKSPACE_STATUS_NO_DATA_FILE = 3
WORKSPACE_STATUS_MISSING_SCHEMA_FILES = 4
WORKSPACE_STATUS_JSON_FILE_CORRUPTED = 5


class DCCXMLValidator:

    def __init__(self, path_to_workspace: Optional[str] = None, workspace_init: bool = True):
        """
        DCCXMLValidator can be used to validate the DCC against the schema. Online validation is supported,
        where the dcc schema is downloaded from the source specified in the dcc. It is also possible to validate
        the dcc against locally stored schemas. These are stored in a workspace.

        :param path_to_workspace: set path to workspace, if not set then a default workspace path is used.
            Path depends on os.
        :type path_to_workspace: string
        :param workspace_init:  Init the workspace if it has not yet been
            initiated or is not valid.
        :type workspace_init: bool
        """

        #  set workspace where schemas will be stored locally on the machine. Used to perform offline schema validation
        if path_to_workspace is None:
            self.path_workspace = get_standard_workspace_path()
        else:
            self.path_workspace = path_to_workspace

        self.path_data_file = os.path.join(self.path_workspace, "data.json")

        # check if workspace is valid
        self.workspace_status = self.__get_workspace_status()

        self.data: Optional[Data] = None

        # if workspace is not valid try to initiate it
        if workspace_init and not self.workspace_status == WORKSPACE_STATUS_OK:
            self.__init_workspace()
            self.workspace_status = self.__get_workspace_status()

        # if workspace is valid load data.json. These file contains alls local available schemas
        if self.workspace_status == WORKSPACE_STATUS_OK:
            with open(self.path_data_file, mode="r", encoding="utf-8") as file:
                self.data = Data(**json.load(file))

        self.previous_used_schmas = {}

    def __init_workspace(self):
        # Create a Readme.txt file inside the Folder with some information about the usage.

        content = "This directory was created by the pyDCC software.\nIt is used to store downloaded xml schemas." \
                  "\nThese are used for the validation of the DCCs." + "\n\n" + "Created on: " + \
                  str(datetime.now())
        path_readme = os.path.join(self.path_workspace, 'Readme.txt')
        if not os.path.exists(path_readme):
            with open(path_readme, mode="w") as file:
                file.write(content)

        self.__download_list_with_available_releases()

        self.__download_schemas_referenced_by_list()

        self.__download_dependencys()

        if self.data is not None:
            with open(self.path_data_file, mode="w") as file:
                file.write(self.data.json(indent=4))

    def __get_workspace_status(self) -> int:
        """
        Check the workspace.

        1. Test if the path to the workspace folder exists and user have access
        2. Test if there is a Readme.txt file inside the workspace
        3. Test if there is a data.json file insode the workspace
        4. Try to parse the data.json file
        5. Test if all loacal xsd files referenced ba data.json exists

        :return: Status of workspace (WORKSPACE_STATUS_OK,WORKSPACE_PATH_DOES_NOT_EXIST,WORKSPACE_NO_README
        ,WORKSPACE_STATUS_NO_DATA_FILE,WORKSPACE_STATUS_MISSING_SCHEMA_FILES,WORKSPACE_STATUS_JSON_FILE_CORRUPTED)
        :rtype: int
        """

        # 1. Test if the path to the workspace folder exists
        if not os.path.exists(self.path_workspace):
            return WORKSPACE_PATH_DOES_NOT_EXIST

        if not os.access(self.path_workspace, os.W_OK | os.R_OK):
            raise PermissionError("Check the choosen workspace directory " + "\"" + str(
                self.path_workspace) + "\"" + " but the current user has no access rights")

        # 2. Test if there is a Readme.txt file inside the workspace
        if not os.path.isfile(os.path.join(self.path_workspace, "Readme.txt")):
            return WORKSPACE_NO_README

        # 3. Test if there is a data.json file insode the workspace
        if not os.path.isfile(os.path.join(self.path_workspace, "data.json")):
            return WORKSPACE_STATUS_NO_DATA_FILE

        # 4. Try to parse the data.json file
        with open(self.path_data_file, mode="r", encoding="utf-8") as file:
            try:
                self.data = Data(**json.load(file))
            except ValidationError:
                return WORKSPACE_STATUS_JSON_FILE_CORRUPTED

            # return "can not parse data.json file"

        # 5. Test if all local xsd files referenced ba data.json exists
        for local_schema in self.data.local_available_schemas:
            if not os.path.isfile(local_schema.location_local_abs):
                return WORKSPACE_STATUS_MISSING_SCHEMA_FILES

        return WORKSPACE_STATUS_OK

    def dcc_is_valid_against_schema(self, dcc_etree: ET, dcc_version: str,
                                    online: bool) -> bool:
        """
        Validate DCC against the dcc schema

        :param dcc_etree: XML etree object build from dcc.xml
        :param dcc_version: version of teh dcc in case of online = False
        :param online: download referenced dcc schemas using location hints or use local stored xsd files
        :return: true if dcc is valid
        """

        if online:
            return xmlschema.is_valid(xml_document=dcc_etree, use_location_hints=True)
        else:

            if dcc_version in self.previous_used_schmas:
                schema = self.previous_used_schmas[dcc_version]
                return xmlschema.is_valid(xml_document=dcc_etree, schema=schema, use_location_hints=False)

            schema_info: Optional[Schema] = None

            if self.data is not None:
                for local_available_schema in self.data.local_available_schemas:
                    if local_available_schema.version_str == dcc_version:
                        schema_info = local_available_schema
                        break
            else:
                raise DccSchemaNotAvailableLocal

            if schema_info is None:
                raise DccSchemaNotAvailableLocal

            with open(schema_info.location_local_abs, 'r') as file:
                schema_file = file.read()

            local_schema_locations = {"https://ptb.de/dcc": schema_info.location_local_abs}

            for dependency in schema_info.dependencys:
                for local_available_schema in self.data.local_available_schemas:
                    if local_available_schema.online_schemaLocation == dependency:
                        local_schema_locations[
                            local_available_schema.targetNamespace] = local_available_schema.location_local_abs

            schema = xmlschema.XMLSchema(schema_file, build=True, allow="sandbox",
                                         base_url=self.path_workspace,
                                         locations=local_schema_locations)

            self.previous_used_schmas[dcc_version] = schema

            return xmlschema.is_valid(xml_document=dcc_etree, schema=schema, use_location_hints=False)

    def __download_list_with_available_releases(self):

        download = requests.get(url_dcc_schema_releases, allow_redirects=True)
        self.data = Data()
        self.data.online_available_releases = DCCOnlineReleases(**(download.json()))

    def __download_schemas_referenced_by_list(self):

        for release in self.data.online_available_releases.releases:
            if release.type != "stable":
                continue

            download = requests.get(release.url, allow_redirects=True)

            # save downloaded xsd schema content to file
            filename = "dcc_" + release.version.replace(".", "_") + ".xsd"
            with open(os.path.join(self.path_workspace, filename), mode="wb") as file:
                file.write(download.content)

            schema = Schema(targetNamespace=get_target_namespace_from_xml((download.content.decode("utf-8"))),
                            filename=filename,
                            version_str=release.version,
                            location_local_abs=str(os.path.join(self.path_workspace, filename)),
                            online_schemaLocation=release.url,
                            dependencys=get_imports_from_xml((download.content.decode("utf-8"))))

            self.data.local_available_schemas.append(schema)

    def __download_dependencys(self):

        # The schemas are uniquely identified by their schemaLocation. However, the generated filename cannot be
        # unique if the schemaLocation changes but the schema does not. For this reason an uid was introduced.
        # Another solution would be the use of a hash value.
        uid = 0

        for local_dcc_schema in self.data.local_available_schemas:
            for dependecny in local_dcc_schema.dependencys:
                try:
                    download = requests.get(dependecny, allow_redirects=True)
                except Exception as e:
                    print(e)
                    continue
                # save downloaded xsd schema content to file
                # check for xml content
                if "<?xml" not in download.content.decode("utf-8")[0:10]:
                    continue

                target_namespace = get_target_namespace_from_xml(download.content.decode("utf-8"))
                version = get_schema_version(download.content.decode("utf-8"))

                uid += 1
                filename = target_namespace.split("/")[-1] + "_" + version.replace(".", "__") + str(uid) + ".xsd"
                with open(os.path.join(self.path_workspace, filename), mode="wb") as file:
                    file.write(download.content)

                new_schema = Schema(targetNamespace=target_namespace,
                                    filename=filename,
                                    version_str=version.replace(".", "_"),
                                    location_local_abs=str(os.path.join(self.path_workspace, filename)),
                                    online_schemaLocation=dependecny)

                # INFO: if you have to download the dependencies of the dependencies (and so on)
                # add dependencys=get_imports_from_xml((download.content.decode("utf-8")) and
                # run this loop until now more schemas will be downloaded

                already_added = False

                for schema in self.data.local_available_schemas:
                    if schema.online_schemaLocation == new_schema.online_schemaLocation:
                        already_added = True
                        break

                if not already_added:
                    self.data.local_available_schemas.append(new_schema)
