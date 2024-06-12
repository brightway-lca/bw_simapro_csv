from ..utils import add_amount_or_formula, skip_empty
from .base import SimaProCSVBlock


class TechnosphereEdges(SimaProCSVBlock):
    def __init__(self, block: list[tuple], header: dict, category: str, **kwargs):
        """Parse a block representing inputs or outputs (avoided production).

        Has the form:

        ```
        Materials/fuels
        Soy oil, refined, at plant/kg/RNA;kg;0;Undefined;0;0;0;

        ```

        Each edge data line has the form:

        0. name
        1. unit
        2. value or formula
        3. uncertainty type
        4. uncert. param.
        5. uncert. param.
        6. uncert. param.
        7. comment

        """
        self.category = category
        self.parsed = []
        self.has_formula = True

        for line_no, line in skip_empty(block):
            self.parsed.append(
                add_amount_or_formula(
                    {
                        "name": line[0],
                        "unit": line[1],
                        "kind": line[3],
                        "field1": line[4],
                        "field2": line[5],
                        "field3": line[6],
                        "comment": line[7],
                        "line_no": line_no,
                    },
                    line[2],
                    header["decimal_separator"],
                )
            )
