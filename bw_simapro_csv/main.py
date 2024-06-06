import csv
import os
from io import StringIO
from pathlib import Path
from typing import List, Union

# Makes `sloppy-windows-1252` encoding available
import ftfy
from loguru import logger

from .blocks import DatabaseInputParameters, Process, ProjectInputParameters, SimaProCSVBlock, Units, LiteratureReference, Method
from .errors import IndeterminateBlockEnd
from .header import parse_header
from .utils import BeKindRewind, clean


def dummy(data, *args):
    return data


CONTROL_BLOCK_MAPPING = {
    "Database Calculated parameters": dummy,
    "Database Input parameters": DatabaseInputParameters,
    "Literature reference": LiteratureReference,
    "Project Input parameters": ProjectInputParameters,
    "Project Calculated parameters": dummy,
    "Quantities": dummy,
    "Product stage": dummy,
    "Units": Units,
    "Process": Process,
    "Method": Method,
    "Impact category": dummy,
    "Normalization-Weighting set": dummy,
    "Damage category": dummy,
}

# These are lists of flows at the end of the file
INDETERMINATE_SECTION_HEADERS = {
    "Non material emissions": dummy,
    "Airborne emissions": dummy,
    "Waterborne emissions": dummy,
    "Raw materials": dummy,
    "Final waste flows": dummy,
    "Emissions to soil": dummy,
    "Social issues": dummy,
    "Economic issues": dummy,
    "System description": dummy,
}

INDETERMINE_SECTION_ERROR = """
    Flow lists are given at the end of this file, but the section headings for
    flow lists are also used in inventory process descriptions. We can normally
    use the text 'End' to show when a process block stops, but this file doesn't
    seem to use 'End' sections. We therefore can't tell if '{}' is a new block
    or not, and can't parse this file.
"""


class SimaProCSV:
    def __init__(
        self, path_or_stream: Union[Path, StringIO], encoding: str = "sloppy-windows-1252"
    ):
        """Read a SimaPro CSV file object, and parse the contents.

        We start with the header, as this defines how the rest of the file is to be parsed.
        It gives the CSV delimiter and decimal separator.

        We then break the file into logical chunks, such as processes or LCIA impact categories."""
        if isinstance(path_or_stream, Path):
            if not path_or_stream.is_file():
                raise ValueError(f"Given `Path` {path_or_stream} is not a file")
            if not os.access(path_or_stream, os.R_OK):
                raise ValueError(f"File {path_or_stream} exists but lacks read permission")
            data = (line for line in open(path_or_stream, encoding=encoding))
        elif not isinstance(path_or_stream, StringIO):
            raise ValueError(
                f"`path_or_stream` must be `Path` or `StringIO` - got {type(path_or_stream)}"
            )
        else:
            # We have to assume that the StringIO object was created with
            # some reasonable newline definition.
            data = (line for line in path_or_stream)
        # Converting Pydantic back to dict to release memory
        self.header = parse_header(data).model_dump()
        self.uses_end_text = False

        logger.info(
            "SimaPro CSV import started.\n\tFile: {file}\n\tDelimiter: {delimiter}\n\tName: {name}",
            file=path_or_stream if isinstance(path_or_stream, Path) else "StringIO",
            delimiter="<tab>" if self.header["delimiter"] == "\t" else self.header["delimiter"],
            name=self.header["project"] or "(Not given)",
        )

        if self.header["delimiter"] not in {";", ".", "\t", "|", " "}:
            logger.warning(f"SimaPro CSV file uses unusual delimiter '{self.header['delimiter']}'")

        rewindable_csv_reader = BeKindRewind(
            csv.reader(data, delimiter=self.header["delimiter"], strict=True), strip=True
        )
        self.blocks = self.generate_blocks(rewindable_csv_reader)

    def generate_blocks(self, rewindable_csv_reader: BeKindRewind) -> List[SimaProCSVBlock]:
        data = []

        while True:
            try:
                block = self.get_next_block(rewindable_csv_reader)
                if block:
                    data.append(block)
            except StopIteration:
                break

        return data

    def get_next_block(self, rewindable_csv_reader: BeKindRewind) -> Union[None, SimaProCSVBlock]:
        data = []

        for line in rewindable_csv_reader:
            if not any(line):
                # Skip empty lines at beginning of block
                continue
            if len(line) == 1 and line[0] == "End":
                # Empty block
                self.uses_end_text = True
                return
            break
        else:
            # Already at end of file
            raise StopIteration

        block_type = line[0]
        if block_type in CONTROL_BLOCK_MAPPING:
            block_class = CONTROL_BLOCK_MAPPING[block_type]
        elif block_type in INDETERMINATE_SECTION_HEADERS:
            if not self.uses_end_text:
                raise IndeterminateBlockEnd(INDETERMINE_SECTION_ERROR.format(block_type))
            block_class = INDETERMINATE_SECTION_HEADERS[block_type]
        else:
            raise ValueError(f"Can't process unknown block type {block_type}")

        for line in rewindable_csv_reader:
            if line and line[0] == "End":
                self.uses_end_text = True
                return block_class(data, self.header) if data else None
            if line and line[0] in CONTROL_BLOCK_MAPPING:
                rewindable_csv_reader.rewind()
                return block_class(data, self.header) if data else None
            data.append(line)

        # EOF
        return block_class(data, self.header) if data else None
