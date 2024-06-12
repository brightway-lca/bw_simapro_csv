from typing import List

from ..utils import asnumber, jump_to_nonempty, skip_empty
from .base import SimaProCSVBlock


class DamageCategory(SimaProCSVBlock):
    def __init__(self, block: List[tuple], header: dict):
        """Parse a `Damage category` block.

        Damage categories are not normalization or weighting, but an aggregation of impact
        categories.

        Has the form:

        ```
        Damage category
        NORM - Ecosystems   PDFm3d

        Impact categories
        NORM - Eco - Freshwater 0.5
        NORM - Eco - Marine 0.5
        NORM - Eco - Terrestrial    0.5
        ```

        There is one definition line with the form:

        0. Damage category name
        1. unit

        In the `Impact categories` definition, each line has the form:

        0. Impact category name
        1. conversion factor

        """
        self.parsed = {"impact_categories": []}

        block = jump_to_nonempty(block)
        self.parsed["name"], self.parsed["unit"] = block.pop(0)[1]

        block = jump_to_nonempty(block)
        assert block.pop(0)[1] == ["Impact categories"]

        for line_no, line in skip_empty(block):
            self.parsed["impact_categories"].append(
                {"name": line[0], "factor": asnumber(line[1]), "line_no": line_no}
            )
