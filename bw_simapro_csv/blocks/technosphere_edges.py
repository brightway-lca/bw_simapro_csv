from ..utils import skip_empty
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
        self.raw = []

        for line_no, line in skip_empty(block):
            self.raw.append(
                {
                    "name": line[0],
                    "unit": line[1],
                    "value_raw": line[2],
                    "kind": line[3],
                    "field1": line[4],
                    "field2": line[5],
                    "field3": line[6],
                    "comment": line[7],
                    "line_no": line_no,
                }
            )
