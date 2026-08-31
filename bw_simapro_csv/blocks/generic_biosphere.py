from typing import Any, List

from ..cas import validate_cas_string
from ..errors import UnparsableLine
from ..utils import add_amount_or_formula, skip_empty
from .base import SimaProCSVBlock


def check_line_length(line: list, expected: int, category: str, line_no: int) -> None:
    """Raise a helpful error if `line` is too short to be a data row.

    A short row is normally an unrecognized block heading which was given to the previous
    block as data, so say so instead of raising a bare `IndexError`."""
    if len(line) < expected:
        raise UnparsableLine(
            f"""
    Line {line_no} in block '{category}' has {len(line)} fields, but at least {expected} are
    needed. This is usually an unrecognized block heading being read as a data row.
    Line content:
    	{line}
        """
        )


class GenericBiosphere(SimaProCSVBlock):
    def __init__(self, block: List[tuple], header: dict, category: str):
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
        self.parsed = []

        for line_no, line in skip_empty(block):
            check_line_length(line, 4, category, line_no)
            self.parsed.append(
                {
                    "name": line[0],
                    "unit": line[1],
                    "cas_number": validate_cas_string(line[2]),
                    "comment": line[3],
                    "line_no": line_no,
                }
            )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SimaProCSVBlock):
            return self.parsed == other.parsed and self.category == getattr(other, "category")
        return False


class GenericUncertainBiosphere(GenericBiosphere):
    def __init__(self, block: List[list], header: dict, category: str):
        """Parse a generic biosphere block with uncertainty.

        Applies to all of the following:

        * Economic issues
        * Emissions to air
        * Emissions to soil
        * Emissions to water
        * Final waste flows
        * Non material emissions
        * Resources
        * Social issues

        Note and enjoy how these category labels are slightly different than `GenericBiosphere`.

        Has the form:

        ```
        Category label
        Data line

        ```

        Each data line has the form:

        0. name
        1. subcategory
        2. unit
        3. value or formula
        4. uncertainty type
        5. uncert. param.
        6. uncert. param.
        7. uncert. param.
        8. comment

        In previous versions, the index of units and values could be switched. This doesn't appear
        to be the case anymore.

        """
        self.category = category
        self.parsed = []
        self.has_formula = True

        for line_no, line in skip_empty(block):
            check_line_length(line, 8, category, line_no)
            self.parsed.append(
                add_amount_or_formula(
                    {
                        "name": line[0],
                        "context": (self.category, line[1]),
                        "unit": line[2],
                        "kind": line[4],
                        "field1": line[5],
                        "field2": line[6],
                        "field3": line[7],
                        "line_no": line_no,
                    },
                    line[3],
                    header["decimal_separator"],
                )
            )
