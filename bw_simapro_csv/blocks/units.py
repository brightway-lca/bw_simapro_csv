from typing import List

from ..utils import asnumber
from .base import SimaProCSVBlock


class Units(SimaProCSVBlock):
    def __init__(self, block: List[list], header: dict, offset: int):
        """Parse a `Units` block.

        Each line has the form:

        0. name
        1. dimension
        2. conversion factor (float)
        3. reference unit

        The block header label is already stripped."""
        self.parsed = []
        self.offset = offset

        for line in block:
            if not any(line):
                continue
            self.parsed.append(
                {
                    "name": line[0],
                    "dimension": line[1],
                    "conversion": asnumber(line[2], header.get("decimal_separator", ".")),
                    "reference unit name": line[3],
                }
            )
