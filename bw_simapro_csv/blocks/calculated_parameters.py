from typing import List

from ..utils import normalize_number_in_formula
from .base import SimaProCSVBlock


class DatabaseCalculatedParameters(SimaProCSVBlock):
    def __init__(self, block: List[list], header: dict, offset: int):
        """Parse an `Database Calculated parameters` block.

        Has the form:

        ```
        Database Calculated parameters
        empty;1/load;
        m1;"Iff(m=1; 1; 0)";
        Conv_STon_MTon;2/2,20462;Convert short ton  (U.S. ton) to metric ton (tonne)
        ```

        Each line has the form:

        0. label
        1. formula
        2. comment

        """
        self.parsed = []
        self.offset = offset

        for index, line in enumerate(block, start=offset):
            if not line or not any(line):
                continue
            self.parsed.append(
                {
                    "label": line[0],
                    "formula": normalize_number_in_formula(
                        line[1], header.get("decimal_separator", ".")
                    ),
                    "comment": line[2],
                }
            )


class ProjectCalculatedParameters(DatabaseCalculatedParameters):
    """Same as format and layout as `DatabaseCalculatedParameters`"""

    pass
