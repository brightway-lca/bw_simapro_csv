# bw_simapro_csv

[![PyPI](https://img.shields.io/pypi/v/bw_simapro_csv.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/bw_simapro_csv.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/bw_simapro_csv)][pypi status]
[![License](https://img.shields.io/pypi/l/bw_simapro_csv)][license]

[![Read the documentation at https://bw_simapro_csv.readthedocs.io/](https://img.shields.io/readthedocs/bw_simapro_csv/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/brightway-lca/bw_simapro_csv/actions/workflows/python-test.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/brightway-lca/bw_simapro_csv/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/bw_simapro_csv/
[read the docs]: https://bw_simapro_csv.readthedocs.io/
[tests]: https://github.com/brightway-lca/bw_simapro_csv/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/brightway-lca/bw_simapro_csv
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Installation

You can install _bw_simapro_csv_ via [pip] from [PyPI] or conda/mamba from the channel `cmutel`:

```console
$ pip install bw_simapro_csv
```

## Usage

`bw_simapro_csv` extracts a single SimaPro separated value export file to a series of blocks. Files can be CSV, TSV, or some other separator.  Basic usage:

```python
from pathlib import Path
from bw_simapro_csv import SimaProCSV
sp = SimaProCSV(Path("my SimaPro file.csv"))
```

The file object must be an instance of `pathlib.Path` or `io.StringIO`. The `SimaProCSV` will do the following:

* Determine the file type. There are three kinds of SimaPro export files: "processes", "methods", and "product stages". This library **does not** yet work with product stages.
* Read the header, and build `SimaProCSV.header`. The header is a dictionary of metadata. We do our best to convert the values to their python equivalents, such as datetimes or booleans.
* Using the metadata, read the rest of the file, and convert it into a series of blocks. Each block has its own data schema, though they are mostly similar.
* While reading the file, some common data mistakes are cleaned up. For example, impossible uncertainty distributions are switch to `UnkownUncertainty`. We also do our best to create valid and reasonable unicode text.
* Many numeric values can be defined by formulae. In order to parse these formulae in python, we need to substitute some operators for their python equivalents (e.g. `**` instead of `^`). As python is case-sensitive, we switch all variable names to upper case, and add the prefix `SP_`, so `my_variable` would become `SP_MY_VARIABLE`. We then evaluate all formulas, and store their numeric results in the `amount` field.

The end result is `SimaProCSV.blocks`, a list of `SimaProCSVBlock` instances with parsed and cleaned data.

## Logging

`bw_simapro_csv` uses the [loguru](https://github.com/Delgan/loguru) library for controlling logs. By default, logs are printed to `stderr`.

## Blocks

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide][Contributor Guide].

## License

Distributed under the terms of the [MIT license][License],
_bw_simapro_csv_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue][Issue Tracker] along with a detailed description.


<!-- github-only -->

[command-line reference]: https://bw_simapro_csv.readthedocs.io/en/latest/usage.html
[License]: https://github.com/brightway-lca/bw_simapro_csv/blob/main/LICENSE
[Contributor Guide]: https://github.com/brightway-lca/bw_simapro_csv/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/brightway-lca/bw_simapro_csv/issues
