# Python library for handling digital calibration certificates (DCC) 

Library for handling DCCs according to the official DCC release [1].

This project is a joint initiative driven by the project [GEMIMEG-II.}(https://www.digitale-technologien.de/DT/Navigation/DE/ProgrammeProjekte/AktuelleStrategischeEinzelprojekte/gemimeg2/gemimeg2.html)

Maintainer: Andreas Tobola (Siemens)

Contributors: Contributors will be listed here

License: [Apache 2.0](LICENSE.md) (proposal)

## Background to DCC

The digital calibration certificate (DCC) is the machine-readable counterpart of the previous calibration certificate. The DCC was releasd by the   Physikalisch-Technische Bundesanstalt (PTB) [1]. The DCC has a hierarchical structure and consists of regulated areas, whose information must meet certain requirements. The DCC exists in Extensible Markup Language (XML). 
## Aim of this software library

Python is a programming language widly used in science and cloud computing applications. This software library extends Python by capabilitie of handling DCC. In particular, loading DCCs from XML-Files, and operating on regulated areas of the DCC. Regulated areas in DCC are (1) administrative data and (2) measurements results. 

```python
import dcc
xml_file_name = '../data/siliziumkugel.xml' # Example file
dcci = dcc.dcc(xml_file_name) # Load DCC from file
```

## Library API


```python
beginPerformanceDate
```


## References


[1] Official release of the digital calibration certificate (DCC) https://www.ptb.de/dcc/v2.4.0/de/

[2] XML shema for DCCs https://www.ptb.de/dcc/dcc.xsd

