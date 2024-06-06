from typing import List

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
        self.parsed = {}

        key, state = None, None

        for line in block:
            if state != "key" and not any([elem.strip() for elem in line]):
                continue
            elif state == "key":
                self.parsed[key] = line[0] if line else None
                state = None
            else:
                key, state = line[0], "key"
