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
sys.path.append("../src/")
from dcc import dcc

# (1) Load DCC and create the DCC object (dcco)
#dcco = dcc('../data/Uncertainty5_PyDCC.xml')
#dcco=dcc('../data/Kugelnormal_ExpUnc_DKD_min_ID.xml')
#dcco = dcc('../data/MFC_2022_02_09.xml')
dcco = dcc('../data/PMM-G_2021-09-15.xml')
# (2) Get some Uncertainties of the DCC from DCC object
#list_with_uncertainties = dcco.uncertainty_list()

list_with_uncertainties = dcco.uncertainty_list_KJ()
mandLang = dcco.mandatoryLang()


# (N) Print data
print('mandatory language %s' % mandLang)

for j in list_with_uncertainties:
    print(j)

