from ..utils import skip_empty
from .base import SimaProCSVBlock


class Products(SimaProCSVBlock):
    def __init__(self, block: list[tuple], header: dict, **kwargs):
        """Parse a `Products` block.

        Has the form:

        ```
        Products
        my product;kg;0,5;100;not defined;Agricultural;

        ```

        Each data line has the form:

        0. name
        1. unit
        2. amount
        3. allocation
        4. waste type
        5. category
        6. comment

        """
        self.raw = []

        for line_no, line in skip_empty(block):
            self.raw.append(
                {
                    "name": line[0],
                    "unit": line[1],
                    "value_raw": line[2],
                    "allocation_raw": line[3],
                    "waste_type": line[4],
                    "category": line[5],
                    "comment": line[6],
                    "line_no": line_no,
                }
            )
