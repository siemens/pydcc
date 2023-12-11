
# Python library supporting automated processing of digital calibration certificates (DCC) 

[![PyPI version](https://badge.fury.io/py/pydcc.svg)](https://badge.fury.io/py/pydcc) [![CI test](https://github.com/siemens/pydcc/actions/workflows/ci-test.yml/badge.svg)]([https://badge.fury.io/py/pydcc](https://github.com/siemens/pydcc/actions/workflows/ci-test.yml))

PyDCC is an open-source project released under the MIT license, accelerating application development for processing Digital Calibration Certificates (DCC), according to the official DCC release [3]. 
This collaborative work was introduced by a talk given at the 2nd DCC conference [4]. 
Further, an introduction video [6] exists, looking briefly at the contents of a DCC and demonstrating PyDCC's essential features by implementing an example application from scratch.
Note that to process DCC automatically, data within the DCC must follow particular format requirements defined by Good Practice [5].

Out of scope: PyDCC is not intended to modify or generate DCCs. PyDCC is a read-only library. For this purpose, other tools and libraries exist.

## General Software Information

This software module is a joint initiative driven by the project [GEMIMEG-II.](https://www.digitale-technologien.de/DT/Navigation/DE/ProgrammeProjekte/AktuelleStrategischeEinzelprojekte/gemimeg2/gemimeg2.html)

Maintainer: [Andreas Tobola](mailto:pydcc.t@siemens.com), Siemens AG

Contributors: The workflow was defined in the [contribution guide](CONTRIBUTING.md). We appreciate any contributions.

## License

The software was generally licensed under the [MIT License](LICENSE). Therefore, see the LICENSE file in the top-level directory.

[Data examples](data) included in this repository may contain other licenses. Please refer to the license declarations within the data examples.

## Background to DCC

The digital calibration certificate (DCC) is the machine-readable counterpart of the previous calibration certificate. The DCC was released by the Physikalisch-Technische Bundesanstalt (PTB) [1]. The DCC has a hierarchical structure comprising regulated areas whose information must meet specific requirements. The DCC exists in Extensible Markup Language (XML). 

## Aim of this software library

Python is a programming language widely used in science and cloud computing applications. This software library extends Python by capabilities of handling DCC, in particular, loading DCCs from XML-Files, and operating on regulated areas of the DCC. Regulated areas in DCC are (1) administrative data and (2) measurement results. 

Consider reading the [user guide](doc/pydcc.md) for more details, including API documentation.

## Installation

```
pip install pydcc
```

## Official Code Repository

Location of the official code repository: https://github.com/siemens/pydcc/

The [contibution guide](CONTRIBUTING.md) explains how one can contribute to this software module.

## Initial Contributors

This project was started in January 2021 with an initial team of developers.

* [Andreas Tobola](@tobola), [Siemens AG](https://siemens.com)
* [Kai Mienert](@mienertPTB), [PTB](https://www.ptb.de)
* [Katharina Janzen](@katharina.janzen), [PTB](https://www.ptb.de)
* [Anupam Prasad Vedurmudi](@vedurmudiPTB), [PTB](https://www.ptb.de)
* [Caroline Bender](@cbender), [Deutsche Telekom Security GmbH](https://www.telesec.de)
* [Robin Fay](@FayR-DTSEC), [Deutsche Telekom Security GmbH](https://www.telesec.de)
* [Tobias Messinger](@tobias.messinger), Digiraster (affiliation until April 2022)
* [Andreas Mucha](@andreas.mucha), [Siemens AG](https://siemens.com)

Besides coding, the weekly team discussions were essential for achieving our goals. 
Additional discussion supporters were:

* Daniel Heißelmann, [PTB](https://www.ptb.de)
* Benjamin Gloger, [PTB](https://www.ptb.de)

## References

[1] The official release of the digital calibration certificate (DCC) in version 2.4.0 https://www.ptb.de/dcc/v2.4.0/de/

[2] Current XML schema for DCCs https://www.ptb.de/dcc/dcc.xsd

[3] The official release of the digital calibration certificate (DCC) in version 3.2 https://www.ptb.de/dcc

[4] Andreas Tobola, Introducing PyDCC – a Python module for the DCC, 2nd international DCC-Conference 01 - 03 March 2022 Proceedings, Publisher: Physikalisch-Technische Bundesanstalt (PTB), DOI 10.7795/820.20220411, 2022

[5] Good Practice for DCC https://dccwiki.ptb.de/en/gp_home

[6] Andreas Tobola, [PyDCC Introduction Video](https://www.linkedin.com/feed/update/urn:li:activity:7130481024207081472/), 2023, Brief look at the contents of a DCC and demonstrate PyDCC's essential features by implementing an example application from scratch.

## Links

* Main page to the DCC https://www.ptb.de/dcc
* Gitlab.com repository with the scheme https://gitlab.com/ptb/dcc/xsd-dcc
* Gitlab.com repository with the good practice https://gitlab.com/ptb/dcc/dcc-goodpractice