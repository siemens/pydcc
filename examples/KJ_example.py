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
sys.path.append("../dcc/")
from dcc import DCC
# (1) Load DCC and create the DCC object (dcco)
#dcco = DCC('../data/dcc/siliziumkugel_2_4_0.xml')
dcco = DCC('../data/Uncertainty5_PyDCC.xml')
#dcco = DCC('../data/TestDCCs/si_elements/si_complex1_PyDCC.xml')
#dcco =DCC('../data/KMT/Kugelnormal_ExpUnc_2022_03_02.xml')

print("mandatory language")
lang = dcco.mandatoryLang()
print(lang)

print("single result")

res = dcco.get_calibration_result_by_quantity_id("MeasRes1_res1_quant1")
print(res)

print("all results")
res = dcco.get_calibration_results('en')
for i in res:
   print(i)

#res = dcco.uncertainty_list()
#print('uncertainty list')
#for i in res:
#    print(i)






