from ..utils import asnumber, skip_empty
from .base import SimaProCSVBlock


class WasteTreatment(SimaProCSVBlock):
    def __init__(self, block: list[tuple], header: dict, **kwargs):
        """Parse a `Waste treatment` block.

        Has the form:

        ```
        Waste treatment
        Aluminium scrap, post-consumer {GLO};kg;-1;All waste types;Metals\\Market;comment here
        ```

        Each data line has the form:

        0. name
        1. unit
        2. amount
        3. waste type
        4. category
        5. comment

        """
        self.parsed = []

        for line_no, line in skip_empty(block):
            self.parsed.append(
                {
                    "name": line[0],
                    "unit": line[1],
                    "amount": asnumber(line[2], decimal_separator=header["decimal_separator"]),
                    "waste_type": line[3],
                    "category": line[4],
                    "comment": line[5] if len(line) > 5 else None,
                    "line_no": line_no,
                }
            )


class WasteScenario(WasteTreatment):
    pass


class SeparatedWaste(SimaProCSVBlock):
    def __init__(self, block: list[tuple], header: dict, **kwargs):
        """Parse a `Separated waste` block.

        Has the form:

        ```
        Separated waste
        Scrap aluminium {RoW};Aluminium;100;comment

        ```

        Each data line has the form:

        0. waste treatment
        1. waste type
        2. fraction (percentage)
        3. comment

        """
        self.parsed = []

        for line_no, line in skip_empty(block):
            self.parsed.append(
                {
                    "waste_treatment": line[0],
                    "waste_type": line[1],
                    "amount": asnumber(line[2], decimal_separator=header["decimal_separator"]),
                    "comment": line[3] if len(line) > 3 else None,
                    "line_no": line_no,
                }
            )


class RemainingWaste(SeparatedWaste):
    pass
