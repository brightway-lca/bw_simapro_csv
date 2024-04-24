import itertools
from collections.abc import Iterator
from typing import List


def clean(s: str) -> str:
    """Strip string and remove ASCII delete character"""
    return s.replace("\x7f", "").strip()


def nobraces(s: str) -> str:
    """Remove braces from header section elements"""
    return s[s.find("{") + 1 : s.rfind("}")]


def noquotes(s: str) -> str:
    """Remove string start/end characters"""
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


def asboolean(s: str) -> bool:
    """Convert SimaPro strings to actual booleans"""
    if s.lower() in {"yes", "y", "true", "t", "1"}:
        return True
    if s.lower() in {"no", "n", "false", "f", "0"}:
        return False
    # Better raise an error then assume we understand SimaPro
    raise ValueError(f"Can't convert '{s}' to boolean")


class BeKindRewind(Iterator):
    """CSV generator which allows for one step backwards"""

    def __init__(self, g: Iterator, strip: bool = False):
        self.g = g
        self.current = None
        self.strip = strip

    def __next__(self) -> List[str]:
        self.current = next(self.g)
        if self.strip:
            return [elem.strip() for elem in self.current]
        else:
            return self.current

    def rewind(self) -> None:
        if self.current is None:
            return
        self.g = itertools.chain((self.current,), self.g)
        self.current = None
