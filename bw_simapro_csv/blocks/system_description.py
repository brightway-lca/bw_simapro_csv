from typing import List

from ..utils import alternating_key_value
from .base import SimaProCSVBlock


class SystemDescription(SimaProCSVBlock):
    def __init__(self, block: List[list], header: dict):
        """Parse a `System description` block.

        Each block as the form:

        key
        value

        with empty lines in between, e.g.

        ```
        System description

        Name
        Ecoinvent v3

        Category
        Others

        Description
        long text

        End
        ```

        """
        self.parsed = dict(alternating_key_value(block))
