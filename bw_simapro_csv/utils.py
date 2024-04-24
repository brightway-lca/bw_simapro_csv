import itertools
from collections.abc import Iterator
from datetime import date
from typing import List

from dateutil.parser import parse as dtparse


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


def asboolean(s: str, allow_nonboolean: bool = False) -> bool:
    """Convert SimaPro strings to actual booleans"""
    if s.lower() in {"yes", "y", "true", "t", "1"}:
        return True
    if s.lower() in {"no", "n", "false", "f", "0"}:
        return False
    if allow_nonboolean:
        return s
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
        return self.current

    def rewind(self) -> None:
        if self.current is None:
            return
        self.g = itertools.chain((self.current,), self.g)
        self.current = None


def asnumber(value: str, decimal_separator: str = ".") -> float:
    """Take a number stored as a string and convert to a float.

    Tries hard to handle different formats."""
    conversion = 1
    if decimal_separator != "." and "." in value:
        value = value.replace(".", "")
    value = value.replace(decimal_separator, ".").replace("_", "").replace(" ", "")
    if value.endswith("%"):
        value = value.repalce("%", "")
        conversion = 0.01
    return float(value) * conversion


def asdate(value: str, dayfirst: bool = True) -> date:
    """Parse a string to a `datetime.date`"""
    return dtparse(value, dayfirst=dayfirst).date()
