# PyDCC user guide

User guide for those who want to use PyDCC for their application.

## Installing the PyDCC library

Usually, we would use PyPi for distributing and isntalling our open source software. 
```python
python install pydcc
```

However, we decided to pospone the publication of our software module. Thus, we have to use this alternateve.
```python
git pull
git checkout <version>
python setup.py bdist
pip install -e .
```

Explanation of the steps:
- Make sure beeing in the root from the git repository.
- git pull to get the latest changes.
- git checkout followed by the version you want to install. Versions are declared in the README.md.
- python setup.py bdist to build the projects. You will need to install setuptools therefore: pip install setuptools
- pip install -e . to install pydcc on a local machine.

## Loading an DCC from file

DCCs were defined as XML files [1]. The code below loads an example provided by the PTB. By loading the XML file will be loaded and translated to an object structure.

```python
import dcc
dcco = dcc.dcc('siliziumkugel.xml') # Load DCC from file
```

## Library API

Returns True, if the DCC was loaded successfully.
```python
is_loaded()
```

Verify DCC file according to the official XML shema [2] 
```python
verify_dcc_xml_file()
```

Retruns True, if the DCC was signed?
```python
is_signed()
```

Retruns True, if DCC signature valid?
```python
is_signature_valid()
```

Returns calibration date as datetime object. Note that the DCC defines the start date (beginPerformanceDate) and the end date (endPerformanceDate) of calibration. The date retured by this API reffers to the end of calibration (endPerformanceDate).
```python
calibration_date()
```

Returns the number of days since calibration (endPerformanceDate). This function was designed for checking the calibration date against the requirements of a quality management system (QMS). A QMS may define a maximum number of days until a device has to be calibrated.
```python
days_since_calibration()
```
