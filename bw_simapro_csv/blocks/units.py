from typing import List

from ..utils import asnumber, skip_empty
from .base import SimaProCSVBlock


class Units(SimaProCSVBlock):
    def __init__(self, block: List[list], header: dict):
        """Parse a `Units` block.

        Each line has the form:

        0. name
        1. dimension
        2. conversion factor (float)
        3. reference unit

        The block header label is already stripped."""
        self.parsed = []

        for line_no, line in skip_empty(block):
            self.parsed.append(
                {
                    "name": line[0],
                    "dimension": line[1],
                    "conversion": asnumber(line[2], header.get("decimal_separator", ".")),
                    "reference unit name": line[3],
                    "line_no": line_no,
                }
            )
