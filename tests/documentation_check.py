# Unit tests for PyDCC
#
# Python module for processing of digital calibration certificates (DCC)
# according to https://www.ptb.de/dcc/
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Andreas Tobola <andreas.tobola@siemens.com>
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#
# SPDX-License-Identifier:  MIT
#
import sys
sys.path.append("../dcc")
import dcc

functions_DCC = dir(dcc.DCC)

with open('../doc/pydcc.md') as f:
    documentation = f.read()

found_counter = 0
total_counter = 0

for function in functions_DCC:
    if not function[0] == '_':
        total_counter += 1
        if documentation.find(function) > -1:
            found_counter += 1
        else:
            print(function)

print(" ")
print("%u status::documented" % found_counter)
print("%u status::total " % total_counter)
print("%u status::undocumented" % (total_counter-found_counter))


#print("%u of %u functions are documented" % (found_counter, total_counter))




