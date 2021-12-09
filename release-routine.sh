#!/bin/bash
python3 increase_version.py
pip install -e .

python3 setup.py bdist_egg

cd tests
pytest
cd ..

cd examples
python3 minimal_working_example.py
cd ..

