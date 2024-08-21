from typing import Any, List, Union

from ..utils import alternating_key_value, asboolean
from .base import SimaProCSVBlock


def reformat(v: Union[list, str]) -> Any:
    """Do LCIA Method-specific reformatting to a list or string"""
    if isinstance(v, list):
        return tuple(v)
    else:
        return asboolean(v, allow_nonboolean=True)


class Method(SimaProCSVBlock):
    def __init__(self, block: List[list], header: dict):
        """Parse a `Method` block.

        Each block as the form:

        key
        value

        with empty lines in between, e.g.

        ```
        Method

        Name
        DC Test

        Version
        1   8

        Comment
        Damage category import testing

        Category
        Others\\NORM

        Use Damage Assessment
        Yes

        Use Normalization
        No

        Use Weighting
        No
        ```

        """
        self.parsed = {k: reformat(v) for k, v in alternating_key_value(block)}
