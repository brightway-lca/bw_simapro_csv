from typing import List

from .base import SimaProCSVBlock
from ..cas import validate_cas


class GenericBiosphere(SimaProCSVBlock):
    def __init__(self, block: List[list], header: dict, offset: int, category: str):
        """Parse a generic biosphere block.

        Applies to all of the following:

        * Non material emissions
        * Airborne emissions
        * Waterborne emissions
        * Raw materials
        * Final waste flows
        * Emissions to soil
        * Social issues
        * Economic issues

        Has the form:

        ```
        Category label
        Flow label, flow unit, CAS number, comment

        ```

        In the generic biosphere flow definitions, each line has the form:

        0. flow label
        1. flow unit
        2. flow CAS number
        3. comment

        """
        self.category = category
        self.offset = offset
        self.parsed = []

        for index, line in enumerate(block, start=offset):
            if not line or not any(line):
                continue

            self.parsed.append(
                {
                    "name": line[0],
                    "unit": line[1],
                    "cas_number": validate_cas(line[2]),
                    "comment": line[3],
                    "line_no": index,
                }
            )
