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

# Run tests
cd tests
pytest --cov dcc --cov-branch --cov-report term-missing --cov-report html
cd ..

# Install locally
pip install -e

# Run minimal example
cd examples
python3 minimal_working_example.py
cd ..

# Upgarde or install dev tools
pip install --upgrade  -r .\dev_requirements.txt

# Increase version
python increase_version.py

# Cleanup old package files
rm dist/*.*

# Create packages
python setup.py sdist bdist_wheel --universal

# Upload
twine upload dist/* # --verbose

# Install from package
pip install --upgrade pydcc
