# PyDCC
#
# Minimal working example
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#
import sys
import zlib

sys.path.append("../dcc/")
from dcc import DCC
# (1) Load DCC and create the DCC object (dcco)
#dcco = DCC('../data/dcc/siliziumkugel_2_4_0.xml')
#dcco = DCC('../data/dcc/dcc_gp_temperature_typical_v12.xml')
#dcco = DCC('../data/gp/dcc_gp_temperatur_resistance_v12.xml')
dcco =DCC('../data/gp/dcc_gp_temperature_extensive_v12.xml')
#dcco =DCC('../data/gp/dcc_ngp_temperature_extensive_v12_some_quant_with_same_refType.xml')
#dcco= DCC('../data/dcc/dcc_ngp_temperature_typical_v12_refType2ID.xml')
#dcco= DCC('../data/KMT/Lagerring_2022-07-13.xml')
#dcco = DCC('C:/Users/janzen01/Documents/GEMIMEG/InputKalibrierscheine/DCC3_1_2/VCMM_KMG/VCMM1_param.xml')
#dcco = DCC('C:/Working_D/xml/example/PORTAL_CMM_KJ/Log/VCMM_DCC.xml')

#print("single result")
#res = dcco.get_calibration_result_by_quantity_id("basic_measurementError")
#print(res)
print("all results")
res = dcco.get_calibration_results('de')
for i in res:
   print(i)

res = dcco.get_calibration_result_by_quantity_refType('basic_measurementError')

print("function that extracts information of a quantity with refType: basic_measurementError")
print(res)