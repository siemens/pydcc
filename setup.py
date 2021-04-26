# PyDCC
#
# Setup script for generating PyDCC package
#
# Copyright (c) Siemens AG, 2021
#
# Authors:
#  Andreas Tobola <andreas.tobola@siemens.com>
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#

from setuptools import setup

with open('README.md') as file:
    long_description = file.read()
#long_description = "Library for handling digital calibration certificates (DCCs)."

setup(
    name = "pydcc",
    version = "0.2.1",
    author = "Andreas Tobola",
    author_email = "andreas.tobola@siemens.com",
    description = ("Library for handling digital calibration certificates (DCC). "),
    license = "MIT License",
    keywords = "digital calibration certificate measurement uncertainty precision GUM DCC",
    url = "https://gitlab.com/gemimeg/pydcc",
    package_dir={'': 'src'},
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    install_requires=[
   'xmlschema ~= 1.6.1',
    ]
)