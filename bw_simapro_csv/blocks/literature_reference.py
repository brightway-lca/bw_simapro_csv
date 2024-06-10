from typing import List

from ..utils import alternating_key_value
from .base import SimaProCSVBlock


class LiteratureReference(SimaProCSVBlock):
    def __init__(self, block: List[list], header: dict):
        """Parse a `Literature reference` block.

        Each block as the form:

        key
        value

        with empty lines in between, e.g.

        ```
        Literature reference

        Name
        Erdöl/2007/Jungbluth, N.

        Documentation link
        http://www.ecoinvent.org

        Category
        Ecoinvent

        Description
        Jungbluth, N. (2007) Erdöl.

        End
        ```

        """
        self.parsed = dict(alternating_key_value(block))
