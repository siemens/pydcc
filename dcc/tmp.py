def get_dsi_info_from_dcc_schema(self, dcc_xsd_path: str, raise_errors: bool = True) -> dict:
    # TODO Umschreiben damit kein pfad sondern ein sring verwendet werden kann
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
            download = requests.get(url, allow_redirects=True)
        except Exception as e:
            if raise_errors:
                raise e
            return False

        """Parse data"""
        datax = download.json()
        self.data.releases = DCCReleases(**datax)

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
