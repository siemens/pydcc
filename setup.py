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

from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

with open('next_version.txt', 'r') as file:
    current_version = file.read()

setup(
    name="pydcc",
    version=current_version,
    author="Andreas Tobola",
    author_email="pydcc.t@siemens.com",
    description=("Library for handling digital calibration certificates (DCC). "),
    license="MIT License",
    keywords="digital calibration certificate measurement uncertainty precision GUM DCC",
    url="https://gitlab.com/gemimeg/pydcc",
    packages=['dcc'],
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'xmlschema > 1.5', 'requests', 'signxml >= 3.1.0', 'certvalidator', 'asn1crypto', 'cryptography', 'pydantic'
    ]
)
