import os
from io import StringIO
from pathlib import Path

from .header import parse_header
from .utils import clean


class SimaProCSV:
    """"""

    def __init__(self, path_or_stream: Path | StringIO, encoding: str = "cp1252"):
        if isinstance(path_or_stream, Path):
            if not path_or_stream.is_file():
                raise ValueError(f"Given `Path` {path_or_stream} is not a file")
            elif not os.access(path_or_stream, os.R_OK):
                raise ValueError(
                    f"File {path_or_stream} exists but lacks read permission"
                )
            data = [clean(line) for line in open(path_or_stream, encoding=encoding)]
        elif not isinstance(path_or_stream, StringIO):
            raise ValueError(
                f"`path_or_stream` must be `pathlib.Path` or `io.StringIO` - got {type(path_or_stream)}"
            )
        else:
            # We have to assume that the StringIO object was created with
            # some reasonable newline definition.
            data = [clean(line) for line in path_or_stream]
        self.header = parse_header(data)
