# Generic PWR Open-PSA Models
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14070453.svg)](https://doi.org/10.5281/zenodo.14070454)


<!-- TOC -->
* [Generic PWR Open-PSA Models](#generic-pwr-open-psa-models)
  * [1. OpenPSA Model Exchange Format](#1-openpsa-model-exchange-format)
  * [2. Explanations About Naming](#2-explanations-about-naming-)
  * [3. About Generic PWR v1.2 Model](#3-about-generic-pwr-v12-model)
  * [4. Manipulate or Update Models](#4-manipulate-or-update-models-)
  * [5. Usage](#5-usage)
  * [5. Additional References Related to Synthetic Models](#5-additional-references-related-to-synthetic-models)
<!-- TOC -->

This repository includes generic PWR v1.2 model in OpenPSA XML format. The goals of including these models are to:

- Serve as test cases for various PRA tools, including [Open-PRA](https://github.com/openpra-org/openpra-monorepo).
- Familiarize users with different modeling approaches and formats.
- Provide a reference for PRA model exchange.
- And more.

The repository also maintains a `schema` for the models to give users valuable insights. 

## 1. OpenPSA Model Exchange Format
The [OpenPSA Model Exchange Format (MEF)](https://open-psa.github.io/mef/index.html) 
represents about a decade of effort to develop a format independent of any specific 
quantification engine. The goal was to create a standard that researchers, corporations, and regulators could use collaboratively in an open environment.


## 2. Explanations About Naming 
```SCRAM``` was used to test models before publish, so some arrangements were done to make sure models are solvable through ```SCRAM```.

```SCRAM``` accepts basic event and gate names as strings, it does not accept only numbers even if the number are in string format like ```"1"```.
So, some initials were added while converting the SAPHSOLVE JSON model to OpenPSA MEF model. below are the initials along with explanations are given:

- ```BE``` for Basic Event
- ```G``` for Gate
- ```S``` for Sequence
- ```INIT``` for Initiating Event
- ```FE``` for Functional Event
- ```FT``` for Fault Tree

User keep in mind, 
- ```FE``` should be in order in ```XML``` file.
- ```SAPHSOLVE``` model may include a ```gate``` has only one ```child```, which is not allowed in ```SCRAM```.
Following `basic-event` definition was added to `model-data` to handle this problem:
```xml
<define-basic-event name="BE0">
    <label>TEMP-BE-TO-ADD-GATES-WITH-A-SINGLE-ELEMENT</label>
    <float value="0.000000E+00"/>
</define-basic-event>
```

## 3. About Generic PWR v1.2 Model
Since 1995, Idaho National Laboratory (INL) has developed Standardized Plant Analysis Risk (SPAR) models for the United States (US) Nuclear Regulatory Commission (NRC) to provide critical risk-informed input to the regulatory process.

The generic PWR model is available as a SAPHIRE model, accompanied by a report detailing the foundations of the modeling phenomena and referencing failure data. The current version of the SAPHIRE model is `v1.2`; however, the documented model information corresponds to `v1.0`. This model is continuously evolving, with researchers and PRA practitioners actively working to improve it. 

At present, the model considers various initiating events, including seismic activity, internal flooding, internal fires, hurricanes, high winds, ISLOCA (Interfacing Systems LOCA), upset conditions leading to transients, large break LOCA, loss of CCW (Component Cooling Water), loss of DC bus, loss of feedwater, loss of offsite power, large steam line breaks, medium break LOCA, steam generator tube ruptures, small LOCA, tornadoes, and excessive LOCA.
`v1.0` of the model includes 56 event trees linked with 140 fault trees.

## 4. Manipulate or Update Models 
User can manipulate and update the models based on needs. A list of `basic-event`, and `functional-event` are provided
to help user to better understand models and update whenever needed. For convenience, `markdown` and `csv` formats for the referred lists
are provided in [models](./models) directory.

## 5. Usage
This model can be used to test quantification engines. Additionally, they enable the creation of a verification platform between quantification engines, allowing developers or practitioners to cross-check their results. Moreover, these models serve as a foundation for benchmarking efforts for any quantification tool.


## 5. Additional References Related to Synthetic Models

- E. M. Aras, A. S. Amin Aly Farag, S. T. Wood, and J. T. Boyce, “Refining Processing Engines from SAPHIRE: Initialization of Fault Tree/Event Tree Solver,” Idaho National Laboratory (INL), Idaho Falls, ID (United States), INL/RPT-23-75066-Rev000, Oct. 2023. doi: 10.2172/2203095.
- C. Smith, “Generic Pressurized Water Reactor Model for SAPHIRE,” INL/EXT-21-62553-Rev000, 1804754, Apr. 2021. doi: 10.2172/1804754.
- S. Wood, J. Boyce, E. Aras, A. Farag, and M. Diaconeasa, “Advancing SAPHIRE: Transitioning from Legacy to State-of-Art Excellence,” in Advanced Reactor Safety (ARS), Las Vegas, NV: American Nuclear Society, 2024, pp. 532–541. doi: 10.13182/T130-43357.
- E. Aras, S. Wood, J. Boyce, A. Farag, and M. Diaconeasa, “Enhancing the SAPHIRE Solve Engine: Initial Progress and Efforts,” in Advanced Reactor Safety (ARS), Las Vegas, NV: American Nuclear Society, 2024, pp. 542–551. doi: 10.13182/T130-43361.
- E. M. Aras, “Enhancement Methodology for Probabilistic Risk Assessment Tools through Diagnostics, Optimization, and Parallel Computing,” Doctor of Philosophy, North Carolina State University, Raleigh, North Carolina, 2024. [Online]. Available: https://repository.lib.ncsu.edu/items/bb05f7f5-1cff-4beb-9312-331bc94b0b95
- A. Farag, S. Wood, A. Earthperson, E. Aras, J. Boyce, and M. Diaconeasa, “Evaluating PRA Tools for Accurate and Efficient Quantifications: A Follow-Up Benchmarking Study Including FTREX,” in Advanced Reactor Safety (ARS), Las Vegas, NV: American Nuclear Society, 2024, pp. 573–582. doi: 10.13182/T130-43377.
- E. M. Aras, S. T. Wood, A. S. A. A. Farag, and J. T. Boyce, “Diagnostics and Strategic Plan for Advancing the SAPHIRE Engine,” Idaho National Laboratory, Idaho Falls, ID, INL/COM-23-74428, Aug. 2023. [Online]. Available: https://inldigitallibrary.inl.gov/sites/sti/sti/Sort_67446.pdf
- M. Hamza, A. Tezbasaran, E. Aras, A. S. Farag, and M. A. Diaconeasa, “Model Exchange Methodology Between Probabilistic Risk Assessment Tools: SAPHIRE and CAFTA Case Study,” in 18th International Probabilistic Safety Assessment and Analysis (PSA 2023), Knoxville, TN: American Nuclear Society, 2023, pp. 150–158.


