# PyDCC
#
# Example for processing DCC signatures
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Andreas Tobola, Siemens AG
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#
# SPDX-License-Identifier:  MIT
#
import sys

from dcc.dcc import DCCTrustStore, DCCSignatureError

sys.path.append("../dcc")
from dcc import DCC

# (1) Create trust store and add trusted root and intermediate certificate
trust_store = DCCTrustStore()
trust_store.load_trusted_root_from_file("../data/trusted_certs/root.crt")
trust_store.load_intermediate_from_file("../data/trusted_certs/sub.crt")

try:
    # (1) Load DCC and create the DCC object (dcco)
    dcco = DCC(xml_file_name='../data/dcc/dcc_gp_temperature_typical_v12_v3.2.0_signed_lt.xml', trust_store=trust_store)
    # (2) Verify if DCC is signed
    if not dcco.status_report.is_signed:
        print('DCC is not signed')

    else:
        print('DCC is signed and signature of DCC is valid')

        # (3) Get signing time
        print("Signing time: %s" % dcco.get_signing_time().strftime('%d/%m/%Y %H:%M:%S'))

        # (4) Get signer certificate
        cert = dcco.get_signer_certificate()

        # (5) Get Subject Name of the signer certificate
        print("Subject name of signer certificate: %s" % cert.subject.rfc4514_string())

        # (6) Get validity period of the signer certificate
        print("Signer certificate is valid from: %s" % cert.not_valid_before.strftime('%d/%m/%Y %H:%M:%S'))
        print("Signer certificate is valid to: %s" % cert.not_valid_after.strftime('%d/%m/%Y %H:%M:%S'))


except DCCSignatureError as e:
    print(str(e))






