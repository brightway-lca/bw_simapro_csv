from typing import List

from ..utils import asnumber
from .base import SimaProCSVBlock


class DamageCategory(SimaProCSVBlock):
    def __init__(self, block: List[list], header: dict, offset: int):
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
        self.offset = offset

        line = block.pop(0)
        while not any(line):
            line = block.pop(0)

        self.parsed["name"] = line[0]
        self.parsed["unit"] = line[1]

        assert not block.pop(0)
        assert block.pop(0) == ["Impact categories"]

        for line in block:
            if not any(line):
                continue
            self.parsed["impact_categories"].append(
                {
                    "name": line[0],
                    "factor": asnumber(line[1]),
                }
            )
