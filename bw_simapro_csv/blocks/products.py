from ..utils import add_amount_or_formula, remove_trailing_percentage, skip_empty
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
        3. allocation (a percentage; a trailing `%` is ignored)
        4. waste type
        5. category
        6. comment

        """
        self.parsed = []
        self.has_formula = True

        for line_no, line in skip_empty(block):
            ds = add_amount_or_formula(
                {
                    "name": line[0],
                    "unit": line[1],
                    "waste_type": line[4],
                    "category": line[5],
                    "comment": line[6],
                    "line_no": line_no,
                },
                line[2],
                header["decimal_separator"],
            )
            ds = add_amount_or_formula(
                data=ds,
                value=remove_trailing_percentage(line[3]),
                decimal_separator=header["decimal_separator"],
                amount_key="allocation",
                formula_key="allocation_formula",
            )
            self.parsed.append(ds)
