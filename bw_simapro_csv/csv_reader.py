import itertools
import re
from collections.abc import Iterator
from typing import List

import ftfy

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


class BeKindRewind(Iterator):
    """CSV reader which acts as a line by line iterator but which allows for one step backwards.

    Needed because the file we are consuming will sometimes indicate that a logical block is
    finished by using the control word `End`, but other times won't. In that case, our iterator
    is already in a new block. To make it simple to pass the iterator to the next function
    consuming the new block, we rewind it one line.

    Internally this is implemented by caching the last line read, and using `itertools.chain`
    when needed to prepend the cached line to the iterator.

    Parameters
    ----------
    data_iterable : collections.abc.Iterator
        Iterator which returns lists of strings.
    clean_elements : bool, optional
    Do `[clean(elem) for elem in line]` when returning a new line

    """

    def __init__(self, data_iterable: Iterator, clean_elements: bool = True, offset: int = 0):
        self.data_iterable = data_iterable
        self.current = None
        self.clean_elements = clean_elements
        # Line numbers are 1-indexed
        self.line_no = offset + 1

    def __next__(self) -> List[str]:
        self.current = next(self.data_iterable)
        self.line_no += 1
        if self.clean_elements:
            self.current = [clean(elem) for elem in self.current]
        return self.current

    def rewind(self) -> None:
        """Rewinds the iterator by one step, retrieving the element that was
        just returned by the previous call to `__next__`."""
        self.line_no -= 1
        if self.current is None:
            return
        self.data_iterable = itertools.chain((self.current,), self.data_iterable)
        self.current = None
