# Python module for processing digital calibration certificates (DCC)
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
import datetime
import time

class dcc:
    ''' Initialize object '''
    def __init__(self, xml_file_name = None):
        self.xml_file_name = xml_file_name#
        self.administrative_data = None
        self.measurement_results = None
        self.root = None
        self.valid_signature = False
        self.datetime_file_loaded = datetime.datetime.now()

        if not xml_file_name is None:
            self.load_dcc_from_xml_file(xml_file_name)

    ''' Load DCC from file '''
    def load_dcc_from_xml_file(self, xml_file_name):
        tree = ET.parse(xml_file_name)
        self.root = tree.getroot()
        self.administrative_data = self.root[0] 
        #self.administrative_data = root.findall("./{https://ptb.de/dcc}administrativeData")
        self.measurement_results = self.root[1]
 
        #for child in self.administrative_data:
        #    print(child.tag)
        #    print(child.tag.find("coreData") )
        #    if child.tag.find("coreData") > -1:
        #        print("*")
        #for child in self.measurement_results[0]:
        #    print(child.tag)

        self.valid_signature = self.verify_dcc_xml_file()
        self.signed = False

    ''' DCC was loaded '''
    def is_loaded(self):
        dcc_loaded = not self.root == None
        return dcc_loaded

    ''' Verify DCC file '''
    def verify_dcc_xml_file(self):
        # DCC signature is not defined in GEMIMEG yet
        return False

    ''' Is DCC signed? '''
    def is_signed(self):
        return self.signed

    ''' Is DCC signature valid? '''
    def is_signature_valid(self):
        return self.valid_signature

    ''' Return calibration date (endPerformanceDate) '''
    def calibration_date(self):
        elem = self.root.findall("./{https://ptb.de/dcc}administrativeData/{https://ptb.de/dcc}coreData/{https://ptb.de/dcc}endPerformanceDate")
        date_string = elem[0].text
        daytime_obj = datetime.datetime.strptime(date_string, '%Y-%m-%d')
        return daytime_obj

    ''' Return number of days since calibration (endPerformanceDate) '''
    def days_since_calibration(self):
        dt_now = datetime.datetime.now()
        dt_calibration = self.calibration_date()
        diff_obj = dt_now - dt_calibration
        days_since_calibration = diff_obj.days
        return days_since_calibration
        