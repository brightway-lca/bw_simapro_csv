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

You can install _bw_simapro_csv_ via from [PyPI](https://pypi.org/project/bw-simapro-csv/):

```console
$ pip install bw_simapro_csv
```

Or using conda/mamba from the channel `cmutel`:

```console
$ mamba install -c conda-forge -c cmutel bw_simapro_csv
```

To install with the compatible Brightway libraries via `pip`:

```console
$ pip install "bw_simapro_csv[brightway]""
```

Or via conda/mamba:

```console
$ mamba install -c conda-forge -c cmutel bw_simapro_csv brightway25
```

On MacOS with ARM chips, run instead:

```console
$ mamba install -c conda-forge -c cmutel bw_simapro_csv brightway25_nosolver
```

See the Brightway docs for more on [ARM CPUs and sparse solvers](https://docs.brightway.dev/en/latest/content/installation/index.html#installing-brightway-using-pip).

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
* Many numeric values can be defined by formulae. In order to parse these formulae in python, we need to substitute some operators for their python equivalents (e.g. `**` instead of `^`). As python is case-sensitive, we switch all variable names to upper case, and add the prefix `SP_`, so `my_variable` would become `SP_MY_VARIABLE`. We then evaluate all formulas (including for allocation), and store their numeric results in the `amount` field.

The end result is `SimaProCSV.blocks`, a list of `SimaProCSVBlock` instances with parsed and cleaned data.

## Products versus processes

Despite the presence of a `Products` block in processes, SimaPro doesn't really differentiate between between the two. Therefore, all process datasets should be considered as [`ProcessWithReferenceProduct`](https://github.com/brightway-lca/bw_interface_schemas/blob/5fb1d40587aec2a4bb2248505550fc883a91c355/bw_interface_schemas/lci.py#L83). Consider this quote from the tutorial:

    Process name in SimaPro
    Under the Documentation tab, you can enter the process name. Please note that this is only for
    your own reference and this name is not used anywhere. Processes are identified by the name
    defined under the Input/Output tab in the product section. Therefore, if you want to search for a
    certain process, you should use the product name defined in the Input/Output as the keyword.

## Waste modelling

The intersection of ecoinvent waste models (negative values means things labelled as inputs are outputs, and vice-versa) and SimaPro `Waste treatment` versus `Waste to treatment` make life interesting. The SimaPro model is:

* `Waste treatment` are *inputs*, and indicate that the given process is a waste treatment process, i.e. it does not have a `Products` block, and has the `category_type` `waste treatment`.
* `Waste to treatment` are *outputs*, and indicate that waste is being produced which needs to be treated. Negative amounts in `Waste to treatment` indicate that these wastes are *inputs*, and that this process is a waste treatment process.

We label edges in both `Products` and `Waste treatment` as functional when exporting to Brightway.

## Logging

`bw_simapro_csv` uses the [loguru](https://github.com/Delgan/loguru) library for controlling logs. By default, logs are printed to `stderr`, and two log files are created: `warning.log` for important errors or information messages, and `debug.log`, for a detailed log of operations and resolved data issues.

Log are created in a directory path drawn from the [platformdirs](https://platformdirs.readthedocs.io/en/latest/) library; you can copy them to a more convenient place with `SimaProCSV.copy_log_dir(some_dir)`, where `some_dir` is a `pathlib.Path` directory instance.

## Exporting to Brightway

Process datasets can be exported to a format usable by `bw2io` with `SimaProCSV.to_brightway()`. This returns a Python dictionary, but you can also write this data to a file on disk by passing a `pathlib.Path` instance, i.e.:

```python
from pathlib import Path
from bw_simapro_csv import SimaProCSV
sp = SimaProCSV(Path("my SimaPro file.csv"))
sp.to_brightway(Path("my-export.json"))
```

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
