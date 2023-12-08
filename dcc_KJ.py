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
#import requests


def read_si_real( node, resultname, Us):
    label = node.find("{https://ptb.de/si}label")
    value = node.find("{https://ptb.de/si}value")
    unit = node.find("{https://ptb.de/si}unit")
    exp_unc = node.find("{https://ptb.de/si}expandedUnc")
    cov_int = node.find("{https://ptb.de/si}coverageInterval")
    if not exp_unc == None:
        unc_ex = exp_unc.find("{https://ptb.de/si}uncertainty")
        if not unc_ex == None:
            Us.append([resultname, 'Expanded uncertainty', unc_ex.text, unit.text])
    elif not cov_int == None:
        unc_st = cov_int.find("{https://ptb.de/si}standardUnc")
        if unc_st is not None:
            Us.append([resultname, 'Standard uncertainty', unc_st.text, unit.text])
    else:
        Us.append([resultname, 'si real without info on U', ':-(', ':-('])

def which_si_list(node, resultname):
    for next_node in node:
        if next_node.tag == '{https://ptb.de/si}list':
            which_si_list(next_node, resultname)
        elif next_node.tag == '{https://ptb.de/si}realList':
            print('TODO: take care of  realList')
        elif next_node.tag == '{https://ptb.de/si}complexList':
            print('TODO: take care of complexList')

def which_si_element(node, resultname, Us):
        if node.tag == '{https://ptb.de/si}real':
            read_si_real(node, resultname, Us)
        elif node.tag == '{https://ptb.de/si}list':
            print('TODO take care of si list')
            which_si_list(node, resultname)
        elif node.tag == '{https://ptb.de/si}hybrid':
            print('TODO take care of hybrid')
        elif node.tag == '{https://ptb.de/si}complex':
            print('TODO take care of complex')
        elif node.tag == '{https://ptb.de/si}constant':
            print('TODO take care of constant')

def quantity_or_list(node, result_name, Us):
    if node.tag == '{https://ptb.de/dcc}quantity':
        for nextnode in node:
            which_si_element(nextnode, result_name, Us)
    elif node.tag == '{https://ptb.de/dcc}list':
        for nextnode in node:
            quantity_or_list(nextnode, result_name, Us)
            
class dcc:
    
    def __init__(self, xml_file_name = None, byte_array = None, compressed_dcc = None, url = None):
        # Initialize DCC object  
        self.xml_file_name = xml_file_name
        self.administrative_data = None
        self.measurement_results = None
        self.root = None
        self.valid_signature = False
        self.datetime_file_loaded = datetime.datetime.now()
        self.name_space = dict()
        self.UID = None
        self.signature_section = None
        self.signed = False
        self.schema_sources = []


        # Set default DCC namespaces
        self.add_namespace('dcc', 'https://ptb.de/dcc')
        self.add_namespace('si', 'https://ptb.de/si')
        self.add_namespace('ds', 'http://www.w3.org/2000/09/xmldsig#')

        # Load default schema files
        #self.add_shema_file('../data/schema/dcc_2_4_0.xsd')
        #self.add_shema_file('../data/schema/SI_Format_1_3_1.xsd')

        if not xml_file_name is None:
            self.load_dcc_from_xml_file(xml_file_name)
        elif not byte_array is None:
            self.load_dcc_from_byte_array(byte_array)
        elif not compressed_dcc is None:            
            self.load_compressed_dcc(compressed_dcc)
        elif not url is None:
            self.load_dcc_from_public_server(url)
        else:
            raise Exception('PyDCC: DCC object created without giving an XML source.')

        if not self.root == None:            
            self.administrative_data = self.root[0] 
            #self.administrative_data = root.find("dcc:administrativeData", self.name_space)
            self.measurement_results = self.root[1]
            self.dcc_version = self.root.attrib['schemaVersion']
            #self.valid_xml = self.verify_dcc_xml()
            self.UID = self.uid()            


    def load_dcc_from_xml_file(self, xml_file_name):
        # Load DCC from file
        with open(self.xml_file_name, "rb") as file:
            byte_array = file.read()
            self.load_dcc_from_byte_array(byte_array)


    def load_dcc_from_byte_array(self, byte_array):
        # Load DCC from file
        self.dcc_xml_raw_data = byte_array
        self.root = ET.fromstring(byte_array)


    def load_dcc_from_public_server(self, server_url, server_port = 8085, dcc_id = None, item_id = None):
        success = False
        # Load DCC from server (PROTOTYPE)
        query_address = server_url # + dcc_id # URL encode, special chars
        response = requests.get(query_address)
        if (response.status_code == 200):
        	byte_array = response.content
        	self.load_dcc_from_byte_array(byte_array)
        	success = True
        return success


    def load_compressed_dcc(self, byte_array):
        # Load compressed DCC
        self.dcc_xml_raw_data = zlib.decompress(byte_array)
        self.load_dcc_from_byte_array(self.dcc_xml_raw_data)   
       
    
    def is_loaded(self):
        # Check if DCC was loaded successfully
        dcc_loaded = not self.root == None
        return dcc_loaded


    def add_namespace(self, name_space_label, name_space_url):
        # Add namespace
        self.name_space[name_space_label] = name_space_url


    def add_shema_file(self, file_name):
        # Add SML schema file
        with open(file_name, "r") as file:
            self.schema_sources.append(file.read())


    def verify_dcc_xml(self):
        # Verify DCC file 
        valid_xml = xmlschema.is_valid(self.xml_file_name, self.schema_sources)
        return valid_xml


    def is_signed(self):
        # Is the DCC signed?        
        elem = self.root.find("ds:Signature", self.name_space)        
        self.signed = not elem == None
        self.signature_section = elem
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

    def mandatoryLang(self):
        # Return mandatory Language Code
        elem = self.root.find("dcc:administrativeData/dcc:coreData/dcc:mandatoryLangCodeISO639_1", self.name_space)
        mandatoryLang = elem.text
        return mandatoryLang

    def version(self):       
        # Return DCC version        
        return self.dcc_version

    def uncertainty_list_KJ(self):
        meas_results = self.root.find("dcc:measurementResults", self.name_space)
        unc_list = []
        for meas_result in meas_results:
            meas_result_name = meas_result.find("dcc:name/dcc:content", self.name_space)
            results = meas_result.find("dcc:results", self.name_space)
            for result in results:
                result_name = result.find("dcc:name/dcc:content", self.name_space)
                result_data = result.find("dcc:data", self.name_space)
                for node in result_data:
                    quantity_or_list(node, result_name.text, unc_list)
        return unc_list


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
                if not unc == None:
                    #if not real_val == None:
                    unc_list.append([result_name.text, unc.text])
        return unc_list
    

    def has_previous_report(self):
        # Check for previous report
        # Returns true if available
        self.previous_report = self.root.find("dcc:administrativeData/dcc:coreData/dcc:previousReport", self.name_space)
        previous_report_available = not self.previous_report == None
        return previous_report_available
    

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
