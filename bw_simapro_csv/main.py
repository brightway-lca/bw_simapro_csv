import csv
import os
import warnings
from io import StringIO
from pathlib import Path
from typing import Union, Iterator

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
    "Product stage": None,
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

        rewindable_csv_reader = BeKindRewind(
            csv.reader(data, delimiter=self.header["delimiter"], strict=True),
            strip=True
        )
        self.blocks = list(self.generate_blocks(rewindable_csv_reader))

    def generate_blocks(self, rewindable_csv_reader: BeKindRewind) -> Iterator[SimaProCSVBlock]:
        while True:
            data = []

            # Get first non-empty line in this block
            try:
                line = next(rewindable_csv_reader)
                while not any([elem.strip() for elem in line]):
                    # Skip empty lines
                    line = next(rewindable_csv_reader)
            except StopIteration:
                return

            try:
                block_class = CONTROL_BLOCK_MAPPING[line[0]]
            except KeyError:
                raise KeyError(f"Can't process unknown block type {line[0]}")

            # Skip to next line past block label
            line = next(rewindable_csv_reader)
            while not any([elem.strip() for elem in line]):
                # Skip empty lines
                line = next(rewindable_csv_reader)

            # Seach for end of block; sometimes there is an 'End', but sometimes not
            # Some lines can be empty, but these are still necessary to understand the layout
            while not line or line[0] != "End" or line[0] not in CONTROL_BLOCK_MAPPING:
                data.append(line)
                print(line)
                try:
                    line = next(rewindable_csv_reader)
                except StopIteration:
                    # EOF
                    yield data
                    return

            # End of block, but missing 'End' element, so rewind to get correct label
            # for next block
            if line[0] in CONTROL_BLOCK_MAPPING:
                rewindable_csv_reader.rewind()

            yield data
