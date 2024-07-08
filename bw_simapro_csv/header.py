from datetime import datetime
from enum import Enum
from typing import List, Optional

from dateutil import parser
from loguru import logger
from pydantic import BaseModel

from .utils import asboolean, nobraces, noquotes

# Sometimes they use text labels instead of characters
DELIMITER_MAP = {"semicolon": ";", "tab": "\t", "comma": ","}

BOOLEAN_LABELS = {
    "Convert expressions to constants:": "convert_expressions",
    "Exclude library processes:": "exclude_library_processes",
    "Export platform IDs:": "export_platform_ids",
    "Include sub product stages and processes:": "include_stages",
    "Related objects (system descriptions, substances, units, etc.):": "related_objects",
    "Skip empty fields:": "skip_empty_fields",
    "Skip unused parameters:": "skip_unused_parameters",
}
STRING_LABELS = {
    "CSV Format version:": "csv_version",
    "Date separator:": "date_separator",
    "Decimal separator:": "decimal_separator",
    "Open library:": "open_library",
    "Open project:": "open_project",
    "Project:": "project",
    "Projet:": "project",  # French for extra flavor!?
    "Selection:": "selection",
}


class SimaProCSVType(str, Enum):
    stages = "product stages"
    methods = "methods"
    processes = "processes"


class SimaProCSVHeader(BaseModel):
    simapro_version: str
    kind: SimaProCSVType
    delimiter: str
    project: Optional[str] = None
    csv_version: str
    libraries: List[str] = []
    selection: Optional[str] = None
    open_project: Optional[str] = None
    open_library: Optional[str] = None
    date_separator: Optional[str] = "/"
    dayfirst: Optional[bool] = False
    export_platform_ids: Optional[bool] = None
    skip_empty_fields: Optional[bool] = None
    convert_expressions: Optional[bool] = None
    related_objects: Optional[bool] = None
    include_stages: Optional[bool] = None
    decimal_separator: Optional[str] = "."
    created: Optional[datetime] = None
    exclude_library_processes: Optional[bool] = None


def parse_header(data: List[str]) -> (SimaProCSVHeader, int):
    """
    Read the header section and parse its values. A typical header looks like:

        {SimaPro 8.2.0.0}
        {processes}
        {Date: 10/12/2016}
        {Time: 10:54:47 PM}

    Sometimes these lines can be quoted:

        "{Related objects (system descriptions, substances, units, etc.): Yes}"

    The generic pattern is:

        SimaPro version
        File export type
        Key: value dictionary
        Optional library list

    We parse this into a header dictionary, doing type conversion when necessary.

    """
    parsed = {"libraries": []}

    date = time = dtformat = ""

    for index, line in enumerate(data):
        if not (line.startswith('"{') or line.startswith("{")):
            break

        line = nobraces(line)

        if line.startswith("SimaPro") and ":" not in line:
            parsed["simapro_version"] = line[8:]
        elif line in iter(SimaProCSVType):
            parsed["kind"] = line
        elif line.startswith("CSV separator:"):
            char = line[len("CSV separator:") :].strip()
            parsed["delimiter"] = DELIMITER_MAP.get(char.lower(), char)
        elif line.startswith("Date:"):
            date = line[len("Date:") :].strip()
        elif line.startswith("Short date format:"):
            dtformat = line[len("Short date format:") :].strip()
        elif line.startswith("Time:"):
            time = line[len("Time:") :].strip()
        elif any(line.startswith(found_key := key) for key in BOOLEAN_LABELS):
            parsed[BOOLEAN_LABELS[found_key]] = asboolean(line[len(found_key) :].strip())
        elif any(line.startswith(found_key := key) for key in STRING_LABELS):
            parsed[STRING_LABELS[found_key]] = noquotes(line[len(found_key) :].strip())
        elif line.startswith("Library '"):
            parsed["libraries"].append(noquotes(line[len("Library") :].strip()))
        else:
            logger.warning(f"Can't understand header line (skipping):\n\t{line}")

    if "kind" not in parsed:
        logger.warning(
            """
    Export is missing type (processes, methods, or product stages).
    Using default value of 'processes'
        """
        )
        parsed["kind"] = "processes"

    dayfirst = not (
        date
        and time
        and dtformat
        # Can be 'MM' or 'M'
        and "M" in dtformat
        and "d" in dtformat
        and dtformat.index("M") < dtformat.index("d")
    )
    parsed["dayfirst"] = dayfirst

    try:
        parsed["created"] = parser.parse(f"{date} {time}", dayfirst=dayfirst)
    except parser.ParserError:
        parsed["created"] = datetime.now()

    return SimaProCSVHeader(**parsed), index
