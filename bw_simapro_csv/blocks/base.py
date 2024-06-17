# pylint: disable=too-many-arguments,unused-argument,too-many-return-statements
from typing import Any


class SimaProCSVBlock:
    """Base class for parsing and cleaning logical blocks in a SimaPro CSV file"""

    def __init__(self, data: Any):
        """Used for only testing; overridden in all real subclasses."""
        self.parsed = data

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SimaProCSVBlock):
            return self.parsed == other.parsed
        return False

    def __len__(self) -> int:
        return len(self.parsed)


class EmptyBlock(SimaProCSVBlock):
    """An empty block without content."""
