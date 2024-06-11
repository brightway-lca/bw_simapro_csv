from typing import List

from ..utils import asboolean
from .base import SimaProCSVUncertainBlock


class GlobalInputParameters(SimaProCSVUncertainBlock):
    def __init__(self, block: List[list], header: dict, offset: int):
        """Parse an `Project|Database Input Parameters` block.

        Each line has the form:

        0. name
        1. value (not formula)
        2. uncertainty type
        3. uncert. param.
        4. uncert. param.
        5. uncert. param.
        6. hidden ("Yes" or "No")
        7-X. comment (can include multiple elements)

        The block header label is already stripped."""
        self.parsed = []
        self.offset = offset

        for index, line in enumerate(block, start=offset):
            if not any(line):
                continue
            self.parsed.append(
                self.distribution(*line[1:6], header=header, line_no=index)
                | {
                    "name": line[0],
                    "hidden": asboolean(line[6]),
                    "comment": "\n".join([elem for elem in line[7:] if elem]),
                    "line_no": index,
                }
            )


class DatabaseInputParameters(GlobalInputParameters):
    pass


class ProjectInputParameters(GlobalInputParameters):
    pass
