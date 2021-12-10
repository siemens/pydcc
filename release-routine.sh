#!/bin/bash
# PyDCC setup script for generating PyDCC package
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Andreas Tobola <andreas.tobola@siemens.com>
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#
python3 increase_version.py
pip install -e .

python3 setup.py bdist_egg

cd tests
pytest
cd ..

cd examples
python3 minimal_working_example.py
cd ..

