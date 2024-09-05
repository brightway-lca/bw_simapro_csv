__all__ = (
    "__version__",
    "SimaProCSV",
    "SimaProCSVType",
)

__version__ = "0.2.4"

# Makes `sloppy-windows-1252` encoding available
import ftfy

from .header import SimaProCSVType
from .main import SimaProCSV
