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
dcco = DCC('dcc_gp_temperature_typical_v12.xml') # Load DCC from file
```

In case the DCC was revived from another system as a string or byte array (dcc_byte_array).
```python
dcco = DCC(byte_array = dcc_byte_array) # Load DCC from file
```

In case a compressed DCC was revived, previously compressed by PyDCC (compressed_dcc_byte_array).
```python
dcco = DCC(compressed_dcc = compressed_dcc_byte_array) # Load DCC from file
```

## DCC unique identification

```python
dcco.uid()
```

## DCC version

```python
dcco.version()
```


## Check if DCC was loaded successfully.

```python
if not dcco.status_report.is_loaded:
    print("Error: DCC was not loaded successfully!")
```



## Perform schema verification

The schema verification must be executed after loading the DCC.

Verify DCC file according to the official XML shema [2] when internet connection is available. 
```python
dcco.verify_dcc_xml(online=True)
```

Verify DCC file according to the official XML shema [2] when internet connection is not available. 
In this case, please make sure downloading all required schema files to local repository using the schema downloader class.
```python
dcco.verify_dcc_xml(online=False)
```

## Signature verification

The signature verification is executed automatically if not deactivate explicitly in the constructor.
However, make sure to provide a trust store before creating the DCC object.
```python
trust_store = DCCTrustStore()
trust_store.load_trusted_root_from_file("../data/trusted_certs/root.crt")
trust_store.load_intermediate_from_file("../data/trusted_certs/sub.crt")
dcco = DCC(xml_file_name='../data/dcc/dcc_gp_temperature_typical_v12_signed.xml', trust_store=trust_store)
```
The trust store object can be reused for loading any other DCCs.


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


## Calibration Laboratory Name

Returns the name of the calibration laboratory.
```python
dcco.calibration_laboratory_name()
```


## Links to other documents

Return true if a link to a previous DCC exists.
```python
dcco.has_previous_report()
```



## Uncertainty

Processing of DCC automatically is a key motivation for PyDCC.
Thus, evaluation the uncertainty of an DCC according to specific requirements was evaluated. 
Therefore, please try the example in ../examples/uncertainty_check_example.py


## Compressed DCC

With this example a compressed DCC was generated which can be embedded on a device with constraint resources. 
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



## List of identifications
The available identifications of all the items described by the DCC can be returned using
```python
serial_number = dcco.get_item_id_by_name('Serial no.')
```
Please try the example in ../examples/read_identifications.py




## Get the mendatory language

```python
print( dcco.mandatory_language()
```

Return example: de

