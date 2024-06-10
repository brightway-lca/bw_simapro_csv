from typing import List

from ..utils import asnumber
from .base import SimaProCSVBlock


class NormalizationWeightingSet(SimaProCSVBlock):
    def __init__(self, block: List[list], header: dict):
        """Parse a `Normalization-Weighting set` block.

        Has the form:

        ```
        Normalization-Weighting set
        IMPACT World+ (Stepwise 2006 values)

        Normalization
        Human health;1.37E+01
        Ecosystem quality;1.01E-04

        Weighting
        Human health;5401.459854
        Ecosystem quality;1386.138614
        ```

        There is one definition line with the form:

        0. Normalization and (!?) weighting name

        In the `Normalization` definition, each line has the form:

        0. Impact or damage category name
        1. normalization factor

        In the `Weighting` definition, each line has the form:

        0. Impact or damage category name
        1. weighting factor

        The can be normalization, weighting, or both.

        """
        self.parsed = {"normalization": [], "weighting": []}
        mode, index = None, 0

        while not (line := block[index]):
            index += 1

        self.parsed["name"] = line[0]
        index += 1

        while not (line := block[index]):
            index += 1

        for line in block[index:]:
            if not line or not any(line):
                continue
            elif line[0] == "Normalization":
                mode = "normalization"
            elif line[0] == "Weighting":
                mode = "weighting"
            else:
                self.parsed[mode].append({"category": line[0], "factor": asnumber(line[1])})
