from typing import List

from ..utils import asboolean, asdate
from .base import SimaProCSVBlock

LIST_ELEMENTS = {
    "Avoided products",
    "Economic issues",
    "Electricity/heat",
    "Emissions to air",
    "Emissions to soil",
    "Emissions to water",
    "Final waste flows",
    "Materials/fuels",
    "Non material emissions",
    "Products",
    "Resources",
    "Social issues",
    "Waste to treatment",
    "Waste treatment",
}


class Process(SimaProCSVBlock):
    """A life cycle inventory process, with inputs, products, and elementary exchanges"""

    def __init__(self, block: List[list], header: dict):
        self.parsed = {"metadata": {}}
        self.index = 0

        while not any(block[self.index]):
            self.index += 1

        # Start with metadata. This is stored as:
        # Key
        # Value
        # On separate lines. Also, sometimes Value is missing.
        while block[self.index][0] not in LIST_ELEMENTS:
            k, v = self.pull_metadata_pair(block, header)
            self.parsed["metadata"][k] = v

    def pull_metadata_pair(self, block: List[list], header: dict) -> (str, str):
        key = block[self.index][0]

        if key == "Literature references":
            self.index += 1
            value = []
            while any(block[self.index]):
                reference = {"reference": block[self.index][0]}
                if len(block[self.index]) > 1:
                    reference["comment"] = block[self.index][1]
                value.append(reference)
                self.index += 1
        elif key == "Date":
            value = asdate(block[self.index + 1][0], dayfirst=header["dayfirst"])
            self.index += 2
        elif key == "Infrastructure":
            value = asboolean(block[self.index + 1][0])
            self.index += 2
        else:
            value = (
                " -||- ".join([elem for elem in block[self.index + 1] if elem])
                if block[self.index + 1]
                else ""
            )
            self.index += 2

        # Skip empty lines until next pair. Should only be one line, but life can be surprising
        while not any(block[self.index]):
            self.index += 1

        return key, value
