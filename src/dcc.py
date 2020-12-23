# This python module is inteded to process digital calibration certificates (DCC)
# according to https://www.ptb.de/dcc/
# 
# Supported DCC version v2.4.0
#
# This software was licensed under Apache 2.0 
# https://www.apache.org/licenses/LICENSE-2.0
#
# This project was started in December 23th, 2020 by Siemens AG
# and has been maintained as open source project.

import xml.etree.ElementTree as ET

class dcc:
    ''' Initialize object '''
    def __init__(self, xml_file_name = None):
        self.xml_file_name = xml_file_name#
        self.administrative_data = None
        self.measurement_results = None

        if not xml_file_name is None:
            self.load_dcc_from_xml_file(xml_file_name)

    ''' Load DCC from file '''
    def load_dcc_from_xml_file(self, xml_file_name):
        tree = ET.parse(xml_file_name)
        root = tree.getroot()
        self.administrative_data = root[0]
        self.measurement_results = root[1]
 
        for child in self.administrative_data:
            print(child.tag)
        for child in self.measurement_results[0]:
            print(child.tag)