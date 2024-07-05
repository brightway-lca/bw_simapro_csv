from typing import List

from ..utils import normalize_number_in_formula, skip_empty
from .base import SimaProCSVBlock


class CalculatedParameters(SimaProCSVBlock):
    def __init__(self, block: List[tuple], header: dict, **kwargs):
        """Parse an `{} Calculated parameters` block.

        Has the form:

        ```
        Database Calculated parameters
        empty;1/load;
        m1;"Iff(m=1; 1; 0)";
        Conv_STon_MTon;2/2,20462;Convert short ton  (U.S. ton) to metric ton (tonne)
        ```

        Each line has the form:

        0. name
        1. formula
        2. comment

        """
        self.parsed = []

        for line_no, line in skip_empty(block):
            self.parsed.append(
                {
                    "name": line[0],
                    "formula": normalize_number_in_formula(
                        line[1], header.get("decimal_separator", ".")
                    ),
                    "comment": line[2],
                    "line_no": line_no,
                }
            )


class DatabaseCalculatedParameters(CalculatedParameters):
    pass


class ProjectCalculatedParameters(CalculatedParameters):
    pass


class DatasetCalculatedParameters(CalculatedParameters):
    pass
