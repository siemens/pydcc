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
import os
import xml.etree.ElementTree as ET
import zlib
import binascii
from collections import defaultdict
import requests
from dataclasses import dataclass
from signxml import InvalidCertificate, InvalidSignature, InvalidInput
from certvalidator import CertificateValidator, errors, ValidationContext
from signxml.xades import XAdESVerifier
from asn1crypto import pem
from cryptography import x509
from typing import Union

from typing import Optional
from .dcc_xml_validator import DCCXMLValidator


class DCCStatusType:
    """Status report classes"""
    IS_LOADED = 0
    VALID_SCHEMA = 1
    IS_SIGNED = 2
    VALID_SIGNATURE = 3

@dataclass
class DCCStatusReport:
    """
    Status report for a specific DCC.
    This status report is a checklist represented by a set of binary values.
    This report is created by the class DCC.
    """

    loading_performed: bool = False
    is_loaded: bool = False

    schema_verification_performed: bool = False
    valid_schema: bool = False

    is_signed: bool = False
    signature_verification_performed: bool = False
    valid_signature: bool = False

    def report(self, status_type: DCCStatusType, success=True):
        """Report test results with this method-"""
        if status_type == DCCStatusType.IS_LOADED:
            self.loading_performed = True
            self.is_loaded = success
        elif status_type == DCCStatusType.VALID_SCHEMA:
            self.schema_verification_performed = True
            self.valid_schema = success
        elif status_type == DCCStatusType.IS_SIGNED:
            self.is_signed = success
        elif status_type == DCCStatusType.VALID_SIGNATURE:
            self.signature_verification_performed = True
            self.valid_signature = success
        else:
            raise TypeError("Unknown DCCStatusType was passed to DCCStatusReport.")


    # ignore_list: Optinal[DCCStatusType] = None
    def get_status_summary(self, ignore_list=[]):
        """Read status report summary."""
        overall_status = True

        if DCCStatusType.VALID_SCHEMA not in ignore_list:
            overall_status = overall_status and self.valid_schema

        if DCCStatusType.VALID_SIGNATURE not in ignore_list:
            overall_status = overall_status and self.valid_signature

        return overall_status


class DCCTrustStore:
    def __init__(self):
        self.trust_roots = []
        self.intermediates = []

    def load_trusted_root_from_file(self, file_name):
        cert = None
        with open(file_name, 'rb') as f:
            cert = f.read()
            if pem.detect(cert):
                type_name, headers, der_bytes = pem.unarmor(cert)
                cert = der_bytes
        self.trust_roots.append(cert)

    def load_intermediate_from_file(self, file_name):
        # update trust intermediate list
        cert = None
        with open(file_name, 'rb') as f:
            cert = f.read()
            if pem.detect(cert):
                type_name, headers, der_bytes = pem.unarmor(cert)
                cert = der_bytes
        self.intermediates.append(cert)


class DCC:
    """
    Python module for processing of digital calibration certificates (DCC)
    """

    def __init__(self, xml_file_name=None, byte_array=None, compressed_dcc=None, url=None, trust_store: Union[DCCTrustStore, None] = None ):

        # Initialize DCC object
        self.status_report = DCCStatusReport()
        self.xml_file_name = xml_file_name
        self.administrative_data = None
        self.measurement_results = None
        self.root = None
        self.root_byte = None
        self.datetime_file_loaded = datetime.datetime.now()
        self.name_space = dict()
        self.UID = None
        self.signature_section = None
        self.schema_sources = []
        self.trust_store = trust_store

        self.xml_validator: DCCXMLValidator = DCCXMLValidator()

        # Set default DCC namespaces
        self.add_namespace('dcc', 'https://ptb.de/dcc')
        self.add_namespace('si', 'https://ptb.de/si')
        self.add_namespace('ds', 'http://www.w3.org/2000/09/xmldsig#')
        self.add_namespace('xades', 'http://uri.etsi.org/01903/v1.3.2#')

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
            # self.administrative_data = root.find("dcc:administrativeData", self.name_space)
            self.measurement_results = self.root[1]
            self.dcc_version = self.root.attrib['schemaVersion']
            # self.valid_xml = self.verify_dcc_xml()
            self.UID = self.uid()
            self.status_report.report(DCCStatusType.IS_LOADED)
            if self.is_signed():
                self.status_report.report(DCCStatusType.IS_SIGNED)
                valid_signature = self.__verify_signature()
                self.status_report.report(DCCStatusType.VALID_SIGNATURE, valid_signature)

    def __verify_signature(self):

        if self.trust_store is None:
            print("Could not validate certificate path because of missing trust store")
            return False
        if self.trust_store.trust_roots is None:
            print("Could not validate certificate path because of missing root CA certificate")
            return False
        if self.trust_store.intermediates is None:
            print("Could not validate certificate path because of missing intermediate CA certificate")
            return False

        # Step 1: Validate certificate that was used to sign the DCC
        signing_cert = self.root.find(".//ds:X509Certificate", self.name_space).text
        signing_cert_pem = '-----BEGIN CERTIFICATE-----\n' + signing_cert + '\n-----END CERTIFICATE-----'
        # Vergleich mit dem Digest in Qualified Properties?
        signing_time = self.root.find(".//xades:SigningTime", self.name_space)

        if signing_time is not None:
            validation_time = datetime.datetime.fromisoformat(signing_time.text.replace('Z', '+00:00'))
        else:
            validation_time = datetime.datetime.now()

        # end_entity_cert works, signingCert does not work
        context = ValidationContext(trust_roots=self.trust_store.trust_roots, moment=validation_time)
        validator = CertificateValidator(
            pem.armor('CERTIFICATE', binascii.a2b_base64(str.encode(signing_cert))),
            validation_context=context, intermediate_certs=self.trust_store.intermediates)
        try:
            validator.validate_usage(set())
        except errors.PathValidationError:
            # The certificate could not be validated
            print("Could not validate certificate path")
            return False
            # The certificate could not be validated
        else:
            print("Certificate path is valid")

        # Step 2: Validate DCC signature

        # find the number of References to verify
        num_refs = len(self.root.findall(".//ds:Reference", self.name_space))
        if num_refs < 2:
            print(
                "Expected signed DCC as XadES - but < 2 references are found in the signature (violating ETSI EN 319 "
                "132-1 -> see Table 2)")
            return False

        # try to verify signature using the provided certificate chain (RootCA + SubCA) - signer certificate is
        # parsed from the XML signature
        # caution: at the moment this validation  routine does not include CRL or OCSP validation for the
        # signer certificate or issuing CA - this validation should be implemented in the future to avoid
        # trusting revoked certificates.
        data_to_verify = self.root_byte
        try:
            data = XAdESVerifier().verify(data_to_verify, x509_cert=signing_cert_pem,
                                          expect_references=num_refs)  # expect references due to XADES signature format
            # expect references due to XADES signature format
        except InvalidCertificate as e:
            print("Signing certificate invalid")
            return False
        except InvalidSignature as e:
            print("Signature is invalid")
            return False
        except InvalidInput as e:
            print("Provided XML does not include enveloped signature")
            return False
        else:
            print('signature verified (without CRL or OCSP validation!)')

        # Store signed data from DCC (without enveloped signature) in root element
        # To do: Check if [0] is really the dcc element
        self.root = data[0].signed_xml

        # Store signature from verified xml in signature element
        self.signature_section = data[0].signature_xml

        # Return true if signature was valid, return false if signature was not valid
        return True

    # To do Implement methods
    def get_signer_certificate(self):
        if self.signature_section is None:
            print('No signature section available for this DCC object')
            return None
        signing_cert = self.signature_section.find(".//ds:X509Certificate", self.name_space).text
        if signing_cert is None:
            print('No signer certificate in signature section')
            return None
        signing_cert_pem = '-----BEGIN CERTIFICATE-----\n' + signing_cert + '\n-----END CERTIFICATE-----'
        return x509.load_pem_x509_certificate(str.encode(signing_cert_pem))

    def get_signing_time(self):
        if self.signature_section is None:
            print('No signature section available for this DCC object')
            return None
        signing_time = self.signature_section.find(".//xades:SigningTime", self.name_space)
        if signing_time is None:
            print('No signing time available in signature section')
            return None
        return datetime.datetime.fromisoformat(signing_time.text.replace('Z', '+00:00'))

    def load_dcc_from_xml_file(self):
        # Load DCC from file
        with open(self.xml_file_name, "rb") as file:
            byte_array = file.read()
            self.root_byte = byte_array
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
        return self.status_report.is_loaded

    def add_namespace(self, name_space_label, name_space_url):
        # Add namespace
        self.name_space[name_space_label] = name_space_url

    def verify_dcc_xml(self, online: bool):
        # Verify DCC file
        valid_xml = self.xml_validator.dcc_is_valid_against_schema(self.root, online=online,
                                                                   dcc_version=self.dcc_version)
        self.status_report.report(DCCStatusType.VALID_SCHEMA, valid_xml)
        return valid_xml

    def is_signed(self):
        # Is the DCC signed?
        elem = self.root.find("ds:Signature", self.name_space)
        is_signed = not elem == None
        self.status_report.report(DCCStatusType.IS_SIGNED, is_signed)
        self.signature_section = elem
        return is_signed

    def is_signature_valid(self):
        # Is DCC signature valid?
        return self.status_report.valid_signature

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

    def __read_name(self, node, name, lang):
        local_name = node.find('dcc:name/dcc:content[@lang=' + "\'" + lang + "\'" + ']', self.name_space)
        if local_name is not None:
            name = name + ' ' + local_name.text
        else:
            local_name = node.find('dcc:name/dcc:content', self.name_space)
            if local_name is not None:
                name = name + ' ' + local_name.text
        return name

    def _read_path_realted_info(self, node, attr):
        attr = attr + "dcc:" + str(str(node.tag.rpartition('}')[2]))
        if "refType" in node.attrib.keys():
            attr = attr + " [ @ refType =" + "\'" + str(node.attrib['refType']) + "\'" + "]"
        if "refId" in node.attrib.keys():
            attr = attr + " [ @ refId =" + "\'" + str(node.attrib['refId']) + "\'" + "]"
        if "id" in node.attrib.keys():
            attr = attr + " [ @ id =" + "\'" + str(node.attrib['id']) + "\'" + "]"

        return attr

    def __find_quantities_in_lists(self, node, quant, name, lang, xpath):
        name = self.__read_name(node, name, lang)
        xpath = self._read_path_realted_info(node, xpath)

        if node.tag == '{https://ptb.de/dcc}quantity':
            quant.append([node, name, xpath])
        elif node.tag == '{https://ptb.de/dcc}list':
            xpath = xpath + " //"
            for next_node in node:
                self.__find_quantities_in_lists(next_node, quant, name, lang, xpath)

    def get_calibration_results(self, type, lang=''):
        quantities = []
        res = []
        result_nodes = self.root.findall('dcc:measurementResults/dcc:measurementResult/dcc:results/dcc:result',
                                         self.name_space)
        for result in result_nodes:
            xpath = ".//"
            xpath = self._read_path_realted_info(result, xpath)
            xpath = xpath + " //"

            data_node = result.find('dcc:data', self.name_space)
            name = ''
            name = self.__read_name(result, name, lang)

            for nodes in data_node:
                self.__find_quantities_in_lists(nodes, quantities, name, lang, xpath)

        for quant in quantities:
            si_node = quant[0].find('{https://ptb.de/si}*', self.name_space)
            if si_node is not None:
                if type == 'xpath':
                    local_res = [quant[2], self.etree_to_dict(si_node)]
                else:
                    local_res = [quant[1], self.etree_to_dict(si_node)]
                res.append(local_res)
        return res

    def etree_to_dict(self, t):
        # method to recursively traverse the xml tree from a specified point and to return the elemnts in dictionary form
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

    def get_item_id_by_name(self, searched_name, searched_language = None, searched_issuer = None, ):
        id_list = self.item_id()['identifications']['identification']
        for id in id_list:
            names = id['name']['content']
            issuer = id['issuer']
            if searched_issuer is not None:
                if not issuer == searched_issuer:
                    continue
            for name in names:
                language = name['@lang']
                if searched_language is not None:
                    if not language == searched_language:
                        continue
                name_text =  name['#text']
                if name_text == searched_name:
                    value = id['value']
                    return value
        return None


class dcc(DCC):
    """DEPRECATED compatibility class: please use dcc.DCC"""
    pass
