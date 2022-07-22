# PyDCC
#
# Automated uncertainty verification example
#
# Copyright (c) Siemens AG, 2022
#
# Authors:
#     Andreas Tobola
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#
# This example simulates a machinally verification of uncertainty values.
# Pretending a new calibration has been executed. Usually, the calibration 
# results have to be verified if they meet the requirements for a certain application.
# However, with a DCC this verification can be realized fully automated by computers.

import sys
sys.path.append("../dcc/")
from dcc import DCC
import numpy as np

# Load DCC and create the DCC object (dcco)
dcco = DCC('../data/dcc/dcc_gp_temperature_typical_v12.xml')

#lang = dcco.mandatoryLang()




def calibration_results_pre_processor(cres):

    # Convert calibration result value list from string separated by blanks to lsit of floating point values
    string_list = cres[0].split(' ')
    float_list = []
    for item in string_list:
        float_list.append(float(item))
    cres[0] = float_list

    # Convert uncertainty to floating pint values
    cres[3] = float(cres[3])

    return cres

def search_calibration_results(cres, searched_name):
    for i in cres:
        name = i[0]
        if name.find(searched_name) > -1:
            selected_calib_result = i[1]
            pre_processed_calib_result = calibration_results_pre_processor(selected_calib_result)
            return pre_processed_calib_result


def print_results(cres):
   for i in cres:
      print(i)


cres = dcco.get_calibration_results('en')
print_results(cres)

mres = search_calibration_results(cres, 'Measurement error')
print(mres)


measurement_error_array = mres[0]
# Mean Squared Error
investigated_sensor_mse = np.sum(np.power(measurement_error_array,2)) / len(measurement_error_array)


print("Sensor Mean Squared Error %.4f K" % investigated_sensor_mse)

laboratory_measurement_uncertainty = mres[3]

print("Lab measurement uncertainty %.4f K" % laboratory_measurement_uncertainty)

# Verification of results
uncertainty95_requirement = 0.071
uncertainty95_actual = np.sqrt( laboratory_measurement_uncertainty ** 2  + investigated_sensor_mse ** 2 ) 

print("Total actual uncertainty is %.4f K" % uncertainty95_actual)

print("Total uncertainty requirement is a maximum of %.4f K" % uncertainty95_requirement)
device_meets_requirements = uncertainty95_actual <= uncertainty95_requirement 
print('Device meets requirements:', device_meets_requirements)
