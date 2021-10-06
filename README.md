# Python library for reading and evaluating digital calibration certificates (DCC) 

Library for reading and evaluating digital calibration certificates (DCCs) according to the official DCC version 2.4.0 [1]. Version 3.0.0 [3] is not supported yet.

Out of scope: PyDCC is not inteded to modify or generate DCCs.

## General Software Information

This software module is a joint initiative driven by the project [GEMIMEG-II.](https://www.digitale-technologien.de/DT/Navigation/DE/ProgrammeProjekte/AktuelleStrategischeEinzelprojekte/gemimeg2/gemimeg2.html)

Maintainer: [Andreas Tobola](mailto:andreas.tobola@siemens.com), Siemens AG

Contributors: Contributors will be listed here. If you want to be listed, contact andreas.tobola@siemens.com. We appreciate any contributions. The workflow was defined in the [contribution guide](CONTRIBUTING.md).

## License

In general, the software was licensed under the [MIT License](LICENSE). Therefore, see the LICENSE file in the top-level directory.

[Data examples](data) included in this repository may contain other licenses. Please refer to the license decalrations within the data examples.

## Background to DCC

The digital calibration certificate (DCC) is the machine-readable counterpart of the previous calibration certificate. The DCC was released by the Physikalisch-Technische Bundesanstalt (PTB) [1]. The DCC has a hierarchical structure and consists of regulated areas, whose information must meet certain requirements. The DCC exists in Extensible Markup Language (XML). 
## Aim of this software library

Python is a programming language widly used in science and cloud computing applications. This software library extends Python by capabilities of handling DCC. In particular, loading DCCs from XML-Files, and operating on regulated areas of the DCC. Regulated areas in DCC are (1) administrative data and (2) measurements results. 

For more details including API documentation consider reading the [user guide](doc/pydcc.md).

Further, the [contibution guide](CONTRIBUTING.md) explains how one can contibute to this software module.

## References

[1] Official release of the digital calibration certificate (DCC) in version 2.4.0 https://www.ptb.de/dcc/v2.4.0/de/

[2] XML shema for DCCs https://www.ptb.de/dcc/dcc.xsd

[3] Official release of the digital calibration certificate (DCC) in version 3.0.0 https://www.ptb.de/dcc/v3.0.0/

