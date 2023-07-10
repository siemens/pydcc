# PyDCC
#
# Minimal working example
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Andreas Tobola, Siemens AG
#
# This work is licensed under the terms of the MIT License.
# See the LICENSE file in the top-level directory.
#
# Important note:
# This server is for testing purpose only.
# It is not recommended to run this server in a productive environment.
#
from flask import Flask

app = Flask(__name__)

@app.route('/dcc/123', methods=['GET'])
def dcc_test_service():
    xml_file_name = "../data/dcc/dcc_gp_temperature_typical_v12.xml"
    with open(xml_file_name, "rb") as file:
        byte_array = file.read()
    return byte_array

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, port=8085)


