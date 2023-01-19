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

import xmlschema
import datetime
import xml.etree.ElementTree as ET
import zlib
from collections import defaultdict

#import os

import requests

#os.chdir('C:\PyDCC\pydcc2\pydcc\dcc')

class DCC:

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
        #self.add_schema_file('../data/schema/dcc_3_0_0.xsd')

        #self.add_schema_file('../data/schema/dcc_3_1_2.xsd')
        #self.add_schema_file('../data/schema/dcc_2_4_0.xsd')
        #self.add_schema_file('../data/schema/SI_Format_1_3_1.xsd')
        self.add_schema_file('../data/schema/SI_Format_2.xsd')

        if xml_file_name is not None:
            self.load_dcc_from_xml_file()
        elif byte_array is not None:
            self.load_dcc_from_byte_array(byte_array)
        elif compressed_dcc is not None:
            self.load_compressed_dcc(compressed_dcc)
        elif url is not None:
            self.load_dcc_from_public_server(url)
        else:
            raise Exception('PyDCC: DCC object created without giving an XML source.')

        if self.root is not None:
            self.administrative_data = self.root[0]
            #self.administrative_data = root.find("dcc:administrativeData", self.name_space)
            self.measurement_results = self.root[1]
            self.dcc_version = self.root.attrib['schemaVersion']
            #self.valid_xml = self.verify_dcc_xml()
            self.UID = self.uid()

    def load_dcc_from_xml_file(self):
        # Load DCC from file
        with open(self.xml_file_name, "rb") as file:
            byte_array = file.read()
            self.load_dcc_from_byte_array(byte_array)

    def load_dcc_from_byte_array(self, byte_array):
        # Load DCC from file
        self.dcc_xml_raw_data = byte_array
        self.root = ET.fromstring(byte_array)

    def load_dcc_from_public_server(self, server_url, server_port=8085, dcc_id=None, item_id=None):
        success = False
        # Load DCC from server (PROTOTYPE)
        query_address = server_url  # + dcc_id # URL encode, special chars
        response = requests.get(query_address)
        if response.status_code == 200:
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

    def add_schema_file(self, file_name):
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

    def calibration_laboratory_name(self):
        # Return calibration lab name
        elem = self.root.find("dcc:administrativeData/dcc:calibrationLaboratory/dcc:contact/dcc:name/dcc:content",
                              self.name_space)
        return elem.text

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
        compression_ratio = bytes_compressed / bytes_uncompressed

        # CRC32: crc32(data) & 0xffffffff to generate the same numeric value across all Python versions and platforms.
        dcc_crc32 = zlib.crc32(self.dcc_xml_raw_data) & 0xffffffff

        ret_dict = dict()
        ret_dict['bytes_uncompressed'] = bytes_uncompressed
        ret_dict['bytes_compressed'] = bytes_compressed
        ret_dict['compression_ratio'] = compression_ratio
        ret_dict['dcc_xml_raw_data_compressed'] = dcc_xml_raw_data_compressed
        ret_dict['crc32'] = dcc_crc32

        compressed_dcc_data_in_c = "const uint8_t compressed_dcc[%d] = {" % bytes_compressed
        k = 0
        for byte in dcc_xml_raw_data_compressed:
            k += 1
            hex_str = format(byte, '02x')
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

    def get_calibration_result_by_quantity_refType3(self, result_refType):
        res = []
        #all_res_nodes = self.root.findall('.//{https://ptb.de/dcc}result')
        all_res_nodes = self.root.findall('.//{https://ptb.de/dcc}measurementResult')
        for res_node in all_res_nodes:
            quants = res_node.findall('.//{https://ptb.de/dcc}quantity[@refType=' + "\'" + result_refType + "\'" + ']')
            for quant in quants:
                si_nodes = quant.findall('./{https://ptb.de/si}*')
                for si_node in si_nodes:
                    res.append(self.etree_to_dict(si_node))

        if len(res) > 1:
            return (['more than one qantity has the refType ' + result_refType + '.', res])
        else:
            return (res)

    def get_calibration_result_by_quantity_refType2(self, result_refType):
        res = []
        quants = self.root.findall('.//{https://ptb.de/dcc}quantity[@refType=' + "\'" + result_refType + "\'" + ']')

        if len(quants) > 1:
            return ('more than one quantity has the refType ' + result_refType + '.')

        else:
            for quant in quants:
                si_nodes = quant.findall('./{https://ptb.de/si}*')
                for si_node in si_nodes:
                    res.append(self.etree_to_dict(si_node))
        return(res)

    def get_calibration_result_by_quantity_id(self, result_id):
        node = self.root.find('.//{https://ptb.de/dcc}quantity[@id=' + "\'" + result_id + "\'" + ']')
        res = []
        if node is not None:
            si_nodes = node.findall('./{https://ptb.de/si}*')
            for si_node in si_nodes:
                res = self.etree_to_dict(si_node)
        else:
            res = "quantity with id: " + result_id + "not found in DCC"
        return res

    def __read_name(self, node, name, lang):
        local_name = node.find('dcc:name/dcc:content[@lang=' + "\'" + lang + "\'" + ']', self.name_space)
        if local_name is not None:
            name = name + ' ' + local_name.text
        else:
            local_name = node.find('dcc:name/dcc:content', self.name_space)
            if local_name is not None:
                name = name + ' ' + local_name.text
        return name

    def __find_quantities_in_lists(self, node, quant, name, lang, attr):
        name = self.__read_name(node, name, lang)

        attr = attr + str(str(node.tag) + str(node.attrib))
        if node.tag == '{https://ptb.de/dcc}quantity':
            quant.append([node, name, attr])
        elif node.tag == '{https://ptb.de/dcc}list':
            for next_node in node:
                self.__find_quantities_in_lists(next_node, quant, name, lang, attr)

    def get_calibration_results(self, type, lang=''):
        quantities = []
        res = []
        result_nodes = self.root.findall('dcc:measurementResults/dcc:measurementResult/dcc:results/dcc:result',
                                         self.name_space)
        for result in result_nodes:
            attr = str(str(result.tag) + str(result.attrib))
            data_node = result.find('dcc:data', self.name_space)
            name = ''
            attr = attr + str(str(data_node.tag) + str(data_node.attrib))
            name = self.__read_name(result, name, lang)

            for nodes in data_node:
                self.__find_quantities_in_lists(nodes, quantities, name, lang, attr)

        for quant in quantities:
            si_node = quant[0].find('{https://ptb.de/si}*', self.name_space)
            if si_node is not None:
                if type == 'refType':
                    #local_res = [quant[2], self.etree_to_dict(si_node)]
                    local_res = [quant[0].attrib, self.etree_to_dict(si_node)]
                else:
                    local_res = [quant[1], self.etree_to_dict(si_node)]
                res.append(local_res)
        return res

    def etree_to_dict(self, t):
        #method to recursively traverse the xml tree from a specified point and to return the elemnts in dictionary form
        tkey = t.tag.rpartition('}')[2]
        d = {tkey: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = defaultdict(list)
            for dc in map(self.etree_to_dict, children):
                for k, v in dc.items():
                    dd[k].append(v)
            d = {tkey: {k: v[0] if len(v) == 1 else v
                        for k, v in dd.items()}}
        if t.attrib:
            d[tkey].update(('@' + k, v)
                           for k, v in t.attrib.items())
        if t.text:
            text = t.text.strip()
            if children or t.attrib:
                if text:
                    d[tkey]['#text'] = text
            else:
                d[tkey] = text
        return d

    def item_id(self):
        # Retrieve list of items in DCC and return as a dictionary with identifier type as key
        id_list = self.root.find("dcc:administrativeData/dcc:items/dcc:item/dcc:identifications", self.name_space)
        return self.etree_to_dict(id_list)


class dcc(DCC):
    """DEPRECATED compatibility class: please use dcc.DCC"""
    pass

#if __name__=='__main__':
    #dcco = DCC('../data/dcc/dcc_gp_temperature_typical_v12.xml')
    #res = dcco.get_calibration_result_by_quantity_refType('basic_measurementError')
    #print("function that extracts information of a quantity with refType: basic_measurementError")
    #print(res)
    #print(dcco.verify_dcc_xml())
    #print('done')