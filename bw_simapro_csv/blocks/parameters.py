from typing import List

from ..uncertainty import distribution
from ..utils import asboolean, skip_empty
from .base import SimaProCSVBlock


class InputParameters(SimaProCSVBlock):
    def __init__(self, block: List[list], header: dict, **kwargs):
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

        for line_no, line in skip_empty(block):
            self.parsed.append(
                distribution(
                    *line[1:6], decimal_separator=header["decimal_separator"], line_no=line_no
                )
                | {
                    "name": line[0],
                    "hidden": asboolean(line[6]),
                    "comment": "\n".join([elem for elem in line[7:] if elem]),
                    "line_no": line_no,
                }
            )


class DatabaseInputParameters(InputParameters):
    pass


class ProjectInputParameters(InputParameters):
    pass


class DatasetInputParameters(InputParameters):
    pass
