import csv
import os
import warnings
from io import StringIO
from pathlib import Path
from typing import Union

from .blocks import SimaProCSVBlock
from .header import parse_header
from .utils import BeKindRewind, clean

CONTROL_BLOCK_MAPPING = {
    "Database Calculated parameters": None,
    "Database Input parameters": None,
    "Literature reference": None,
    "Project Input parameters": None,
    "Project Calculated parameters": None,
    "Quantities": None,
    "Units": None,
    "Process": None,
    "Method": None,
    "Impact category": None,
    "Normalization-Weighting set": None,
    "Damage category": None,
}


class SimaProCSV:
    def __init__(self, path_or_stream: Union[Path, StringIO], encoding: str = "cp1252"):
        """Read a SimaPro CSV file object, and parse the contents.

        We start with the header, as this defines how the rest of the file is to be parsed.
        It gives the CSV delimiter and decimal separator.

        We then break the file into logical chunks, such as processes or LCIA impact categories."""
        if isinstance(path_or_stream, Path):
            if not path_or_stream.is_file():
                raise ValueError(f"Given `Path` {path_or_stream} is not a file")
            if not os.access(path_or_stream, os.R_OK):
                raise ValueError(f"File {path_or_stream} exists but lacks read permission")
            data = (clean(line) for line in open(path_or_stream, encoding=encoding))
        elif not isinstance(path_or_stream, StringIO):
            raise ValueError(
                f"`path_or_stream` must be `Path` or `StringIO` - got {type(path_or_stream)}"
            )
        else:
            # We have to assume that the StringIO object was created with
            # some reasonable newline definition.
            data = (clean(line) for line in path_or_stream)
        # Converting Pydantic back to dict to release memory
        self.header = parse_header(data).model_dump()
        if self.header["delimiter"] not in {";", ".", "\t", "|", " "}:
            warnings.warn(f"SimaPro CSV file uses unusual delimiter '{self.header['delimiter']}'")

        data_generator = BeKindRewind(
            csv.reader(data, delimiter=self.header["delimiter"], strict=True),
            strip=True
        )
        self.blocks = [self.pull_block(data_generator)]

    def pull_block(self, data_generator: BeKindRewind) -> SimaProCSVBlock:
        line = next(data_generator)

        while not any([elem.strip() for elem in line]):
            # Skip empty lines
            line = next(data_generator)

        try:
            block_class = CONTROL_BLOCK_MAPPING[line[0]]
        except KeyError:
            raise KeyError(f"Can't understand unknown block type {line[0]}")

        data = []
        line = next(data_generator)

        while line[0] != "End" and line[0] not in CONTROL_BLOCK_MAPPING:
            data.append(line)
            line = next(data_generator)

        # Missing 'End' element
        if line[0] in CONTROL_BLOCK_MAPPING:
            data_generator.rewind()

        return data
