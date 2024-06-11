__all__ = (
    "__version__",
    "SimaProCSV",
)

__version__ = "0.0.1"

# Makes `sloppy-windows-1252` encoding available
import ftfy

from .main import SimaProCSV
