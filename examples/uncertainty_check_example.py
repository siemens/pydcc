# PyDCC
#
# Minimal working example
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#     Andreas Tobola
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#
# This exaple simulates a machinally verifictaion of uncertainty values.
# Pretending a new calibration has been executed. Usually, the calibartion 
# results have to be verified if they meet the requirements for a certain application.
# However, with a DCC this verification can be realized fully automated by computers.

import sys
sys.path.append("../dcc/")
from dcc import DCC

# Load DCC and create the DCC object (dcco)
dcco = DCC('../data/Uncertainty4_PyDCC.xml')

print("mandatory language")
lang = dcco.mandatoryLang()
print(lang)


print("all results")
res = dcco.get_calibration_results('de')
for i in res:
   print(i)







