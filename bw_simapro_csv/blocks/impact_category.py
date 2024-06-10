from typing import List

from ..cas import validate_cas
from ..utils import asnumber
from .base import SimaProCSVBlock


class ImpactCategory(SimaProCSVBlock):
    def __init__(self, block: List[list], header: dict):
        """Parse an `Impact category` block.

        Has the form:

        ```
        Impact category
        NORM - HH - Releases    man.SV

        Substances
        Air (unspecified)   Lead-210    014255-04-0 1.28E-06    kBq
        Water   (unspecified)   Lead-210    014255-04-0 4.03E-09    kBq
        ```

        Each substances line has the form:

        0. category
        1. subcategory
        2. substance name
        3. CAS number (optional)
        4. characterization factor (float)
        5. unit

        """
        self.parsed = {"cfs": []}

        line = block.pop(0)
        while not any(line):
            line = block.pop(0)

        self.parsed["name"] = line[0]
        self.parsed["unit"] = line[1]

        assert not block.pop(0)
        assert block.pop(0) == ["Substances"]

        for line in block:
            if not any(line):
                continue
            self.parsed["cfs"].append(
                {
                    "context": (line[0], line[1]),
                    "name": line[2],
                    "cas_number": validate_cas(line[3]),
                    "factor": asnumber(line[4]),
                    "unit": line[5],
                }
            )
