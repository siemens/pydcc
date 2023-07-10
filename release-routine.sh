#!/bin/bash
# PyDCC setup script for generating PyDCC package
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Andreas Tobola, Siemens AG
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#
set -eux    # abort on error

python3 increase_version.py
pip install -e .

python3 setup.py bdist_wheel

cd tests
pytest --cov dcc --cov-branch --cov-report term-missing --cov-report html
cd ..

cd examples
python3 minimal_working_example.py
cd ..

