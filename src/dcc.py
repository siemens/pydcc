# PyDCC
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

import xml.etree.ElementTree as ET
import xmlschema
import datetime
import time

class dcc:
    
    def __init__(self, xml_file_name = None):
        ''' Initialize object '''
        self.xml_file_name = xml_file_name#
        self.administrative_data = None
        self.measurement_results = None
        self.root = None
        self.valid_signature = False
        self.datetime_file_loaded = datetime.datetime.now()
        self.name_space = {'dcc': 'https://ptb.de/dcc'}
        self.UID = None
        self.xsd_file_path = '../data/dcc_2_4_0.xsd'

        if not xml_file_name is None:
            self.load_dcc_from_xml_file(xml_file_name)             

    
    def load_dcc_from_xml_file(self, xml_file_name):
        # Load DCC from file
        tree = ET.parse(xml_file_name)
        self.root = tree.getroot()
        self.administrative_data = self.root[0] 
        #self.administrative_data = root.find("dcc:administrativeData", self.name_space)
        self.measurement_results = self.root[1]
        self.dcc_version = self.root.attrib['schemaVersion']
        self.valid_xml = self.verify_dcc_xml()
        self.UID = self.uid()
        self.signed = False

    
    def is_loaded(self):
        # Check if DCC was loaded successfully
        dcc_loaded = not self.root == None
        return dcc_loaded

    
    def verify_dcc_xml(self):
        # Verify DCC file 
        try:
            xmlschema.validate(self.xml_file_name, self.xsd_file_path)
            return True
        except:            
            return False


    def is_signed(self):
        # Is the DCC signed?
        return self.signed

    
    def is_signature_valid(self):
        # Is DCC signature valid? 
        return self.valid_signature

    
    def calibration_date(self):       
        # Return calibration date (endPerformanceDate) 
        elem = self.root.find("dcc:administrativeData/dcc:coreData/dcc:endPerformanceDate", self.name_space)
        date_string = elem.text
        daytime_obj = datetime.datetime.strptime(date_string, '%Y-%m-%d')
        return daytime_obj

    
    def days_since_calibration(self):
        # Return number of days since calibration (endPerformanceDate) 
        dt_now = datetime.datetime.now()
        dt_calibration = self.calibration_date()
        diff_obj = dt_now - dt_calibration
        days_since_calibration = diff_obj.days
        return days_since_calibration
        
    
    def uid(self):       
        # Return unique ID 
        elem = self.root.find("dcc:administrativeData/dcc:coreData/dcc:uniqueIdentifier", self.name_space)
        uid_string = elem.text        
        return uid_string

        
    
    def version(self):       
        # Return DCC version
        return self.dcc_version


    
