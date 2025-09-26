# `bw_simapro_csv` Changelog

## [0.4.3] - 2025-09-16

* [#24 - Allow for block headers with one key followed by empty strings](https://github.com/brightway-lca/bw_simapro_csv/pull/24)

## [0.4.2] - 2025-03-09

* Don't issue some duplicate warning messages

## [0.4.1] - 2025-03-09

* Fix [#20 - Waste treatment block amounts can be parametrized](https://github.com/brightway-lca/bw_simapro_csv/issues/20)

## [0.4] - 2025-02-19

* Fix [#18 - Improper termination of CSV file parsing](https://github.com/brightway-lca/bw_simapro_csv/issues/18)

### [0.3.7] - 2025-01-14

* Fix [#17 - Code allow triangular and uniform distributions where mode = minimum = maximum](https://github.com/brightway-lca/bw_simapro_csv/issues/17)

### [0.3.6] - 2025-01-14

* Fix [#16 - Lognormal exchanges with sigma values <= 0](https://github.com/brightway-lca/bw_simapro_csv/issues/16)

### [0.3.5] - 2024-12-11

* [#15 - More robust CAS validation to handle broken inputs](https://github.com/brightway-lca/bw_simapro_csv/pull/15)

### [0.3.4] - 2024-12-05

* Fix missing input argument for name shortening in `SimaProCSV` class method

### [0.3.3] - 2024-12-05

* Making name shortening in MFP name generation configurable

### [0.3.2] - 2024-12-03

* Change `publication_date` type from `datetime.date` to `str` when exporting to Brightway

### [0.3.1] - 2024-11-27

* Add some additional header fields to Brightway export

## [0.3] - 2024-11-25

* Add ability to separate products as separate nodes when exporting to Brightway
* BREAKING CHANGE: Default is now to separate products as separate nodes when exporting to Brightway

### [0.2.6] - 2024-09-10

* Packaging fix

### [0.2.5] - 2024-09-10

* Some header labels and values can be translated

### [0.2.4] - 2024-09-05

* Add better process names on Brightway export

### [0.2.3] - 2024-08-21

* Python 3.9 compatibility

### [0.2.2] - 2024-08-13

* Fix error looking for missing unique code

### [0.2.1] - 2024-07-23

* Handle missing or invalid `Process indentifier` header values
* Move invalid formulae to `invalid_formula`

## [0.2] - 2024-07-09

* Multifunctionality support via `multifunctional`

### [0.1.9] - 2024-07-01

* Make header date and time optional

### [0.1.8] - 2024-07-01

* Allow header without type specification
* Fix `yield` being used in dataset formulas
* Catch Python reserved words in database, project, and dataset formulas
* Add `copy_logs` parameter to `SimaProCSV`
* Catch and log zero division errors
* Correct inheritance tree for calculated parameters
* Correct parsing error with multiple blank lines before end statement

### [0.1.7] - 2024-06-19

* Add checks for issues related to unit conversions

### [0.1.6] - 2024-06-19

* Change default values for missing attributes during Brightway export

### [0.1.5] - 2024-06-18

* Don't replace commas when decimal separator is a `.`, and vice-versa

### [0.1.4] - 2024-06-18

* Allow number with leading digits, e.g. `,8`

### [0.1.3] - 2024-06-17

* Fix parsing of variables with `number underscore number` pattern
* Drop log level of invalid uncertainty distributions
* Provide more context when raising syntax or formula errors

### [0.1.2] - 2024-06-17

Correct Brightway export of product edges and waste treatment functional inputs

### [0.1.1] - 2024-06-17

Packaging fix

## [0.1.0] - 2024-06-17

First release
