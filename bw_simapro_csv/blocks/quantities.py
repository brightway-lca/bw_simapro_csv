from ..utils import asboolean, skip_empty
from .base import SimaProCSVBlock


class Quantities(SimaProCSVBlock):
    def __init__(self, block: list[list], header: dict):
        """Parse a `Quantities` block.

        Each block as the form:

        name, has_dimensions

        For example:

        ```
        Quantities

        Mass; Yes
        Energy; No
        Length; Yes
        ```

        """
        self.parsed = {line[0]: asboolean(line[1]) for _, line in skip_empty(block)}
