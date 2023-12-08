# PyDCC automatic version increment
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Andreas Tobola, Siemens AG
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#

with open('next_version.txt', 'r') as file:
    current_version = file.read()

version_separator = '.'
version_elements = current_version.split(version_separator)

build_version=int(version_elements[2])
build_version += 1
version_elements[2] = str(build_version)
new_version = version_separator.join(version_elements) 
with open('next_version.txt', 'w') as file:
    file.write(new_version)