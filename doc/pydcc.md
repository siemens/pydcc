# PyDCC user guide

User guide for those who want to use PyDCC for their application.

## Installing the PyDCC library

However, we decided to pospone the publication of our software module. Thus, we have to use this alternateve.
```python
git pull
git checkout <version>
python setup.py sdist
pip install -e .
```

Explanation of the steps:
- Make sure beeing in the root from the git repository.
- git pull to get the latest changes.
- git checkout followed by the version you want to install. Versions are declared in the README.md.
- python setup.py bdist to build the projects. You will need to install setuptools therefore: pip install setuptools
- pip install -e . to install pydcc on a local machine.


Usually, we would use PyPi for distributing and isntalling our open source software. 
```python
python install pydcc
```

## Loading an DCC from file

DCCs were defined as XML files [1]. The code below loads an example provided by the PTB. By loading the XML file will be loaded and translated to an object structure.

Load DCC from file
```python
from dcc import dcc
dcco = dcc('siliziumkugel.xml') # Load DCC from file
```

In case the DCC was revived from another system as a string or byte array (dcc_byte_array).
```python
dcco = dcc(byte_array = dcc_byte_array) # Load DCC from file
```

In case a compressed DCC was revived, previously compressed by PyDCC (compressed_dcc_byte_array).
```python
dcco = dcc(compressed_dcc = compressed_dcc_byte_array) # Load DCC from file
```

Returns True, if the DCC was loaded successfully.
```python
dcco.is_loaded()
```

## DCC unique identification

```python
dcco.uid()
```

## DCC version

```python
dcco.version()
```


## Schema Verification

Verify DCC file according to the official XML shema [2] 
```python
dcco.verify_dcc_xml_file()
```

## Signature

Retruns True, if the DCC was signed?
```python
dcco.is_signed()
```

Retruns True, if DCC signature valid?
```python
dcco.is_signature_valid()
```

## Calibration Date

Returns calibration date as datetime object. Note that the DCC defines the start date (beginPerformanceDate) and the end date (endPerformanceDate) of calibration. The date retured by this API reffers to the end of calibration (endPerformanceDate).
```python
dcco.calibration_date()
```

Returns the number of days since calibration (endPerformanceDate). This function was designed for checking the calibration date against the requirements of a quality management system (QMS). A QMS may define a maximum number of days until a device has to be calibrated.
```python
dcco.days_since_calibration()
```


CRC32 of raw data: efc19810

## Links to other documents

Return true if a link to a previous DCC exists.
```python
dcco.has_previous_report()
```



## Uncertainty

A basic list of all uncertainties was implemented so far.
```python
dcco.uncertainty_list()
```

[['Masse', '0.00000005'], ['Volumen', '0.000018']]



## Compressed DCC

With this examle a compressed DCC was generated. 
```python
# Generate compressed DCC
embdcc = dcco.generate_compressed_dcc()   
compression_ratio_100 = embdcc['compression_ratio'] * 100
print('DCC size %d bytes' % embdcc['bytes_uncompressed'])
print('Compressed DCC size %d bytes' % embdcc['bytes_compressed'])
print('Embedded DCC compression ratio %.1f%%' % compression_ratio_100)
print('CRC32 of raw data: %x' % embdcc['crc32'])
compressed_data = embdcc['dcc_xml_raw_data_compressed']
```
In a second step the compressed data (compressed_data) would be transffered to the corresponding sensor system.

Compression results:
The original DCC size for Siliziumkugel.xml in version 2.4.0 was 30926 bytes.
The compressed DCC size was 5324 bytes.
DCC compression ratio 17.2%.