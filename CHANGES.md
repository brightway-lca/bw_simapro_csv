# `bw_simapro_csv` Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.9] - 2024-07-01

* Make header date and time optional

## [0.1.8] - 204-07-01

* Allow header without type specification
* Fix `yield` being used in dataset formulas
* Catch Python reserved words in database, project, and dataset formulas
* Add `copy_logs` parameter to `SimaProCSV`
* Catch and log zero division errors
* Correct inheritance tree for calculated parameters
* Correct parsing error with multiple blank lines before end statement

## [0.1.7] - 204-06-19

* Add checks for issues related to unit conversions

## [0.1.6] - 204-06-19

* Change default values for missing attributes during Brightway export

## [0.1.5] - 204-06-18

* Don't replace commas when decimal separator is a `.`, and vice-versa

## [0.1.4] - 204-06-18

* Allow number with leading digits, e.g. `,8`

## [0.1.3] - 204-06-17

* Fix parsing of variables with `number underscore number` pattern
* Drop log level of invalid uncertainty distributions
* Provide more context when raising syntax or formula errors

## [0.1.2] - 204-06-17

Correct Brightway export of product edges and waste treatment functional inputs

## [0.1.1] - 204-06-17

Packaging fix

## [0.1.0] - 204-06-17

First release
