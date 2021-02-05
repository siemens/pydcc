# Python library for handling digital calibration certificates (DCC) 

Library for handling DCCs according to the official DCC release [1].
## General Software Information

This project is a joint initiative driven by the project [GEMIMEG-II.](https://www.digitale-technologien.de/DT/Navigation/DE/ProgrammeProjekte/AktuelleStrategischeEinzelprojekte/gemimeg2/gemimeg2.html)

Maintainer: Andreas Tobola (Siemens)

Contributors: Contributors will be listed here. If you want to be listed, contact andreas.tobola@siemens.com. We appreciate any contributions. The workflow was defined in the [contribution guide](CONTRIBUTING.md).

## License

In general, the software was licensed under the [The MIT license](LICENSE.md). Therefore, see the LICENSE.md file in the top-level directory.
#
[Data examples](data) included in this repository may contain other licenses. Please reffer to the license decalrations within the data examples.

## Background to DCC

The digital calibration certificate (DCC) is the machine-readable counterpart of the previous calibration certificate. The DCC was releasd by the Physikalisch-Technische Bundesanstalt (PTB) [1]. The DCC has a hierarchical structure and consists of regulated areas, whose information must meet certain requirements. The DCC exists in Extensible Markup Language (XML). 
## Aim of this software library

Python is a programming language widly used in science and cloud computing applications. This software library extends Python by capabilitie of handling DCC. In particular, loading DCCs from XML-Files, and operating on regulated areas of the DCC. Regulated areas in DCC are (1) administrative data and (2) measurements results. 


## Usage

DCCs were defined as XML files [1]. The code below loads an example provided by the PTB. By loading the XML file will be loaded and translated to an object structure.

```python
import dcc
xml_file_name = '../data/siliziumkugel.xml' # Example file
dcci = dcc.dcc(xml_file_name) # Load DCC from file
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


## Unit tests

Unit tests were defined for every API function.

```bash
cd tests
python unit_test.py
```

## References


[1] Official release of the digital calibration certificate (DCC) https://www.ptb.de/dcc/v2.4.0/de/

[2] XML shema for DCCs https://www.ptb.de/dcc/dcc.xsd

