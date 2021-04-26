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
#import xmlschema
import datetime
import time
import zlib

class dcc:
    
    def __init__(self, xml_file_name = None, byte_array = None, compressed_dcc = None):
        # Initialize DCC object  
        self.xml_file_name = xml_file_name
        self.administrative_data = None
        self.measurement_results = None
        self.root = None
        self.valid_signature = False
        self.datetime_file_loaded = datetime.datetime.now()
        self.name_space = {'dcc': 'https://ptb.de/dcc',  'si':'https://ptb.de/si'}
        self.UID = None
        self.xsd_file_path = '../data/dcc_2_4_0.xsd'

        self.schema_sources = []
        with open('../data/dcc_2_4_0.xsd', "r") as f:
            self.schema_sources.append(f.read())
        with open('../data/SI_Format_1_3_1.xsd', "r") as f:
            self.schema_sources.append(f.read())                 

        if not xml_file_name is None:
            self.load_dcc_from_xml_file(xml_file_name)
        elif not byte_array is None:
            self.load_dcc_from_byte_array(byte_array)
        elif not compressed_dcc is None:            
            self.load_compressed_dcc(compressed_dcc)
        else:
            raise Exception('PyDCC: DCC object created without giving an XML source.')

        if not self.root == None:            
            self.administrative_data = self.root[0] 
            #self.administrative_data = root.find("dcc:administrativeData", self.name_space)
            self.measurement_results = self.root[1]
            self.dcc_version = self.root.attrib['schemaVersion']
            #self.valid_xml = self.verify_dcc_xml()
            self.UID = self.uid()
            self.signed = False    

    def load_dcc_from_xml_file(self, xml_file_name):
        # Load DCC from file
        #tree = ET.parse(xml_file_name)
        #self.root = tree.getroot()
        with open(self.xml_file_name, "rb") as f:
            self.load_dcc_from_byte_array(f.read())            


    def load_dcc_from_byte_array(self, byte_array):
        # Load DCC from file
        self.dcc_xml_raw_data = byte_array
        self.root = ET.fromstring(byte_array)


    def load_compressed_dcc(self, byte_array):
        # Load compressed DCC
        self.dcc_xml_raw_data = zlib.decompress(byte_array)
        self.load_dcc_from_byte_array(self.dcc_xml_raw_data)        
        dcc_crc32 = zlib.crc32(self.dcc_xml_raw_data) & 0xffffffff 
        
    
    def is_loaded(self):
        # Check if DCC was loaded successfully
        dcc_loaded = not self.root == None
        return dcc_loaded

    
    def verify_dcc_xml(self):
        # Verify DCC file 
        valid_xml = xmlschema.is_valid(self.xml_file_name, self.schema_sources)
        return valid_xml


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


    def uncertainty_list(self):       
        # Derive uncertainty from DCC
        results = self.root.find("dcc:measurementResults/dcc:measurementResult/dcc:results", self.name_space)
        unc_list = []
        for result in results:
            result_name = result.find("dcc:name/dcc:content", self.name_space)
            result_data_list = result.find("dcc:data/dcc:list", self.name_space)            
            for result_data in result_data_list:
                real_val = result_data.find("si:real/si:value", self.name_space)
                unc = result_data.find("si:real/si:expandedUnc/si:uncertainty", self.name_space)
                if not real_val == None:
                    unc_list.append([result_name.text, unc.text])
        return unc_list
    
    
    def generate_compressed_dcc(self):
        # Convert DCC to C header file for DCC integration on constraint devices

        dcc_xml_raw_data_compressed = zlib.compress(self.dcc_xml_raw_data)
        bytes_uncompressed = len(self.dcc_xml_raw_data)
        bytes_compressed = len(dcc_xml_raw_data_compressed)
        compression_ratio = bytes_compressed/bytes_uncompressed
        
        # CRC32: crc32(data) & 0xffffffff to generate the same numeric value across all Python versions and platforms.
        dcc_crc32 = zlib.crc32(self.dcc_xml_raw_data) & 0xffffffff 

        ret_dict = dict(); 
        ret_dict['bytes_uncompressed'] = bytes_uncompressed
        ret_dict['bytes_compressed'] = bytes_compressed
        ret_dict['compression_ratio'] = compression_ratio
        ret_dict['dcc_xml_raw_data_compressed'] = dcc_xml_raw_data_compressed
        ret_dict['crc32'] = dcc_crc32 
        
        compressed_dcc_data_in_c = "const uint8_t compressed_dcc[%d] = {" % bytes_compressed
        k = 0
        for byte in dcc_xml_raw_data_compressed:
            k += 1
            hex_str = format( byte, '02x')
            hex_str_with_preamble = "0x" + hex_str 
            compressed_dcc_data_in_c += hex_str_with_preamble
            if not k == bytes_compressed:
                compressed_dcc_data_in_c += ", "
            if k % 10 == 0:
                compressed_dcc_data_in_c += "\n"
        compressed_dcc_data_in_c += "};"
        
        compressed_dcc_data_in_c += "\n"
        compressed_dcc_data_in_c += "const uint32_t compressed_dcc_crc32  = 0x%x; // CRC32 according to python module zlib\n" % dcc_crc32
        compressed_dcc_data_in_c += "const uint32_t compressed_dcc_size   = %u; // size in bytes\n" % bytes_compressed
        compressed_dcc_data_in_c += "const uint32_t uncompressed_dcc_size = %u; // size in bytes\n" % bytes_uncompressed

        ret_dict['compressed_dcc_data_in_c'] = compressed_dcc_data_in_c
        return ret_dict
