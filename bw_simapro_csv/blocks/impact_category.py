from typing import List

from ..cas import validate_cas
from ..utils import asnumber, jump_to_nonempty, skip_empty
from .base import SimaProCSVBlock


class ImpactCategory(SimaProCSVBlock):
    def __init__(self, block: List[tuple], header: dict):
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

        block = jump_to_nonempty(block)
        self.parsed["name"], self.parsed["unit"] = block.pop(0)[1]

        block = jump_to_nonempty(block)
        assert block.pop(0)[1] == ["Substances"]

        for line_no, line in skip_empty(block):
            self.parsed["cfs"].append(
                {
                    "context": (line[0], line[1]),
                    "name": line[2],
                    "cas_number": validate_cas(line[3]),
                    "factor": asnumber(line[4]),
                    "unit": line[5],
                    "line_no": line_no,
                }
            )
