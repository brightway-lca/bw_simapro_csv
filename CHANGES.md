# `bw_simapro_csv` Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.3] - 2024-08-21

* Python 3.9 compatibility

## [0.2.2] - 2024-08-13

* Fix error looking for missing unique code

## [0.2.1] - 2024-07-23

* Handle missing or invalid `Process indentifier` header values
* Move invalid formulae to `invalid_formula`

## [0.2] - 2024-07-09

* Multifunctionality support via `multifunctional`

## [0.1.9] - 2024-07-01

* Make header date and time optional

## [0.1.8] - 2024-07-01

* Allow header without type specification
* Fix `yield` being used in dataset formulas
* Catch Python reserved words in database, project, and dataset formulas
* Add `copy_logs` parameter to `SimaProCSV`
* Catch and log zero division errors
* Correct inheritance tree for calculated parameters
* Correct parsing error with multiple blank lines before end statement

## [0.1.7] - 2024-06-19

* Add checks for issues related to unit conversions

## [0.1.6] - 2024-06-19

* Change default values for missing attributes during Brightway export

## [0.1.5] - 2024-06-18

* Don't replace commas when decimal separator is a `.`, and vice-versa

## [0.1.4] - 2024-06-18

* Allow number with leading digits, e.g. `,8`

## [0.1.3] - 2024-06-17

* Fix parsing of variables with `number underscore number` pattern
* Drop log level of invalid uncertainty distributions
* Provide more context when raising syntax or formula errors

## [0.1.2] - 2024-06-17

Correct Brightway export of product edges and waste treatment functional inputs

## [0.1.1] - 2024-06-17

Packaging fix

## [0.1.0] - 2024-06-17

First release
