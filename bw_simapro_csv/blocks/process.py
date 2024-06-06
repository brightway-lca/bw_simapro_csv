import re
from typing import List

from loguru import logger

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
HAS_SUBCATEGORY = {
    "Economic issues",
    "Emissions to air",
    "Emissions to soil",
    "Emissions to water",
    "Final waste flows",
    "Non material emissions",
    "Resources",
    "Social issues",
}
NO_SUBCATEGORY = {
    "Avoided products",
    "Electricity/heat",
    "Materials/fuels",
    "Products",
    "Waste to treatment",
}
PARAMETERS = {
    "Calculated parameters",
    "Input parameters",
}


# Exclude `e` for exponent
has_letters = re.compile("[a-df-zA-CF-Z]+")
has_numbers = re.compile("[0-9]+")


class Process(SimaProCSVBlock):
    """A life cycle inventory process, with inputs, products, and elementary exchanges"""

    def __init__(self, block: List[list], header: dict):
        self.parsed = {"metadata": {}}
        self.raw = {}
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

        # These sections need access to the global variable store
        # before they can be resolved
        while self.index < len(block):
            k, v = self.pull_raw_section(block, header)
            self.raw[k] = v

    def pull_raw_section(self, block: List[list], header: dict) -> (str, list):
        """
        0. name
        1. subcategory
        2. unit (or value)
        3. value or formula (or unit)
        4. uncertainty type
        5. uncert. param.
        6. uncert. param.
        7. uncert. param.
        8. comment

        However, sometimes the value is in index 2, and the unit in index 3. Because why not! We assume default ordering unless we find a number in index 2.
        """
        key = block[self.index][0]
        data = []

        self.index += 1

        while any(block[self.index]):
            if key in HAS_SUBCATEGORY:
                data.append(
                    {
                        "name": a,
                        "context": (key, b),
                        "maybe_unit": c,
                        "maybe_value": d,
                        "kind": e,
                        "field1": f,
                        "field2": g,
                        "field3": h,
                    }
                    for (a, b, c, d, e, f, g, h) in block[self.index]
                )
            self.index += 1

        # Skip empty line ending this section
        self.index += 1

        return key, data

    def resolve_unit_amount(self, a: str, b: str, key: str) -> dict:
        """Determine the unit and amount fields as accurately as possible."""
        # Normally the unit comes first
        if not has_numbers.search(a) and has_numbers.search(b):
            unit, amount = a, b
            self.unit_first = True
        elif has_numbers.search(a) and not has_numbers.search(b):
            unit, amount = b, a
            self.unit_first = False
        # The amount could be a formula with only a variable
        # We don't handle this case for now
        else:
            logger.warning("Ambiguous unit/value pair: '{a}' and '{b}' in section {key}")
            unit, amount = a, b
        if has_letters.search(amount):
            return {"unit": unit, "formula": amount}
        # TBD: Evaulate number
        return {"unit": unit, "amount": float(amount)}

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
