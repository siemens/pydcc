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
laboratory_measurement_uncertainty = mres[3]


print(" ")
print("Measurement uncertainty was +/- %.4f K (2*Sigma)" % laboratory_measurement_uncertainty)

# Verification of results
measurement_error_requirement = 0.1

print(" ")
print("Total uncertainty limits are +/- %.4f K" % measurement_error_requirement)



def measurement_error_evaluation(measurement_error, uncertainty, lower_limit, upper_limit):
	
	lower_limit_extended = lower_limit - uncertainty
	upper_limit_extended = upper_limit + uncertainty
	
	lower_limit_limited = lower_limit + uncertainty
	upper_limit_limited = upper_limit - uncertainty
	
	#if upper_limit_limited <= lower_limit_limited:
	#	print("Limits implicit conditional")
	
	conditional = False
	
	if measurement_error >= lower_limit and measurement_error <= upper_limit:
		passed = True
		if measurement_error < lower_limit_limited or measurement_error > upper_limit_limited:
			conditional = True
		else:
			conditional = False
	else:
		passed = False
		if measurement_error >= lower_limit_extended and measurement_error <= upper_limit_extended:
			conditional = False	
		else:
			conditional = True	

	return (passed, conditional)


overall_passed = True
overall_conditional = False
print ("  MSE   Passed  Cond.") 
for mse in measurement_error_array:	
	passed, conditional = measurement_error_evaluation(mse, laboratory_measurement_uncertainty, -measurement_error_requirement, measurement_error_requirement)
	print("%7.3f %5s  %5s" % ( mse, passed, conditional ) )
	overall_passed = overall_passed and passed 
	overall_conditional = overall_conditional or conditional


print(" ")
print("Overall passed:      %5s" % (overall_passed ) )
print("Overall conditional: %5s" % (overall_conditional) )

device_meets_requirements = overall_passed and not overall_conditional

print('Device meets requirements:', device_meets_requirements)
