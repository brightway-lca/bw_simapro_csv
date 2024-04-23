import warnings
from datetime import datetime
from enum import Enum
from typing import List, Optional

from dateutil import parser
from pydantic import BaseModel

from .utils import asboolean, nobraces, noquotes

# Sometimes they use text labels instead of characters
DELIMITER_MAP = {"semicolon": ";", "tab": "\t", "comma": ","}

BOOLEAN_LABELS = {
    "Export platform IDs:": "export_platform_ids",
    "Skip empty fields:": "skip_empty_fields",
    "Convert expressions to constants:": "convert_expressions",
    "Related objects (system descriptions, substances, units, etc.):": "related_objects",
    "Include sub product stages and processes:": "include_stages",
}
STRING_LABELS = {
    "CSV Format version:": "csv_version",
    "Decimal separator:": "decimal_separator",
    "Selection:": "selection",
    "Open project:": "open_project",
    "Project:": "project",
    "Projet:": "project",  # French for extra flavor!?
    "Date separator:": "date_separator",
}


class SimaProCSVType(str, Enum):
    stages = "product stages"
    methods = "methods"
    processes = "processes"


class SimaProCSVHeader(BaseModel):
    simapro_version: str
    kind: SimaProCSVType
    delimiter: str
    project: str
    csv_version: str
    libraries: List[str] = []
    selection: Optional[str] = ""
    open_project: Optional[str] = ""
    date_separator: Optional[str] = "/"
    export_platform_ids: Optional[bool | None] = None
    skip_empty_fields: Optional[bool | None] = None
    convert_expressions: Optional[bool | None] = None
    related_objects: Optional[bool | None] = None
    include_stages: Optional[bool | None] = None
    decimal_separator: Optional[str] = "."
    created: Optional[datetime] = datetime.now()


def parse_header(data: List[str]) -> SimaProCSVHeader:
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
        key: value dictionary

    We parse this into a header dictionary, doing type conversion when necessary.

    """
    parsed = {"libraries": []}

    for line in data:
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
            warnings.warn(f"Can't understand header line (skipping):\n\t{line}")

    dayfirst = not (
        date
        and time
        and dtformat
        and "MM" in dtformat
        and "dd" in dtformat
        and dtformat.index("MM") < dtformat.index("dd")
    )

    try:
        parsed["created"] = parser.parse(f"{date} {time}", dayfirst=dayfirst)
    except parser.ParserError:
        pass

    return SimaProCSVHeader(**parsed)
