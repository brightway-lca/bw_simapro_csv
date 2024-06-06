import itertools
import re
from collections.abc import Iterator
from copy import copy
from datetime import date
from typing import List

import ftfy
from dateutil.parser import parse as dtparse

UNDEFINED = re.compile("[\x8d\x81\x8f\x90\x9d]")
CONTROL_CHARACTERS = re.compile(
    "[\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16"
    + "\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f]"
)
WARNING_CHARS = "ÃÂ€˜â¿"


def clean(s: str) -> str:
    """Strip string, fix encoding, and remove undefined or control characters"""
    # This makes no sense - /u007f is the delete control character
    # https://www.ascii-code.com/grid
    # But SimaPro uses this as a linebreak inside a CSV line
    # This is why we can't have nice things
    # olca-simapro-csv does the same thing:
    # https://github.com/GreenDelta/olca-simapro-csv/blob/c11e40e7722f2ecaf62e813eebcc8d0793c8c3ff/src/test/java/org/openlca/simapro/csv/CsvLineTest.java#L53
    s = s.replace("\x7f", "\n")
    s = UNDEFINED.sub("", s)
    s = CONTROL_CHARACTERS.sub("", s)
    if any(char in s for char in WARNING_CHARS):
        s = ftfy.fix_text(s)
    return s.strip()


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
            return [clean(elem) for elem in self.current]
        return self.current

    def rewind(self) -> None:
        if self.current is None:
            return
        self.g = itertools.chain((self.current,), self.g)
        self.current = None


def asnumber(value: str, decimal_separator: str = ".", allow_nonnumber: bool = False) -> float:
    """Take a number stored as a string and convert to a float.

    Tries hard to handle different formats."""
    original = copy(value.strip())

    conversion = 1
    if decimal_separator != "." and "." in value:
        value = value.replace(".", "")
    value = value.replace(decimal_separator, ".").replace("_", "").replace(" ", "")
    if value.endswith("%"):
        value = value.replace("%", "")
        conversion = 0.01
    try:
        return float(value) * conversion
    except ValueError as exc:
        if allow_nonnumber:
            return original
        else:
            raise ValueError from exc


def asdate(value: str, dayfirst: bool = True) -> date:
    """Parse a string to a `datetime.date`"""
    return dtparse(value, dayfirst=dayfirst).date()
