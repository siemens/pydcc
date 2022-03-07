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
from dcc import dcc
# (1) Load DCC and create the DCC object (dcco)
#dcco = dcc('../data/dcc/siliziumkugel_2_4_0.xml')
dcco = dcc('../data/Uncertainty5_PyDCC.xml')
#dcco = dcc('../data/TestDCCs/si_elements/si_complex1_PyDCC.xml')

print("mandatory language")
lang = dcco.mandatoryLang()
print(lang)

print("single result")

res = dcco.get_calibration_result_by_quantity_id("MeasRes1_res1_quant1")
print(res)

print("all results")
res = dcco.get_calibration_results()
for i in res:
   print(i)

res = dcco.uncertainty_list()
print('uncertainty list')
for i in res:
    print(i)







# (2) Get some Uncertainties of the DCC from DCC object
#list_with_uncertainties = dcco.uncertainty_list()
#list_with_uncertainties_KJ = dcco.uncertainty_list_KJ()
# (N) Print data

#res = dcco.get_calibration_result_by_quantity_id("DR_M_1")
#print(res)

#print("result of existing uncertainty_list method")
#for j in list_with_uncertainties:
#    print(j)


#print("result of uncertainty_list_KJ method")
#for j in list_with_uncertainties_KJ:
#    print(j)

