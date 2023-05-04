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


def search_calibration_results(cres, searched_reftype):
    for elem in cres:
        xpath_string = elem[0]
        if xpath_string.find(searched_reftype) > -1:
            selected_calib_result = elem[1]
            return selected_calib_result


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

def xml_list_to_float(xml_list: str):
	string_list = xml_list.split(' ')
	float_list = []
	for item in string_list:
		float_list.append(float(item))
	return float_list


def evaluate_measurements_results_for_given_limits(measurement_error_array, laboratory_measurement_uncertainty, measurement_error_requirement):

	print(" ")
	print(" ")
	print("Evaluation with required limits at +/- %.3f K" % measurement_error_requirement)

	overall_passed = True
	overall_conditional = False
	print ("  MSE   Passed  Cond.")
	for mse in measurement_error_array:
		passed, conditional = measurement_error_evaluation(mse, laboratory_measurement_uncertainty, -measurement_error_requirement, measurement_error_requirement)
		print("%7.3f %5s  %5s" % ( mse, passed, conditional ) )
		overall_passed = overall_passed and passed
		overall_conditional = overall_conditional or conditional


	print(" ")
	print("Overall passed:             %5s" % (overall_passed ) )
	print("Overall conditional:        %5s" % (overall_conditional) )

	device_meets_requirements = overall_passed and not overall_conditional

	print('Device meets requirements:  %5s' % device_meets_requirements)

	return device_meets_requirements


if __name__ == '__main__':


	# Load DCC and create the DCC object (dcco)
	dcco = DCC('../data/dcc/dcc_gp_temperature_typical_v12.xml')

	#lang = dcco.mandatory_language()

	# Get calibration results
	cres = dcco.get_calibration_results('xpath')


	# Select data set with measurement error
	mres = search_calibration_results(cres, 'basic_measurementError')
	print(mres)

	# Select array with measurement results
	measurement_error_array = xml_list_to_float(mres['realListXMLList']['valueXMLList'])

	print(measurement_error_array)

	# Select meaasurement uncertainty
	laboratory_measurement_uncertainty = float(mres['realListXMLList']['expandedUncXMLList']['uncertaintyXMLList'])
	print(" ")
	print("Measurement uncertainty was +/- %.4f K (2*Sigma)" % laboratory_measurement_uncertainty)

	# Execute tests with different requirements
	evaluate_measurements_results_for_given_limits(measurement_error_array, laboratory_measurement_uncertainty, 0.1)
	evaluate_measurements_results_for_given_limits(measurement_error_array, laboratory_measurement_uncertainty, 0.16)
	evaluate_measurements_results_for_given_limits(measurement_error_array, laboratory_measurement_uncertainty, 0.18)
