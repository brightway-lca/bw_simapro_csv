from numbers import Number
import numpy as np
from typing import Any, Optional

from loguru import logger


def validate_cas(s: Any) -> Optional[str]:
    ERROR = "CAS Check Digit error: CAS '{}' has check digit of {}, but it should be {}"

    if isinstance(s, str):
        s = s.strip()
    if not s:
        return None
    elif isinstance(s, Number) and np.isnan(s):
        return None

    total = sum((a + 1) * int(b) for a, b in zip(range(9), s.replace("-", "")[-2::-1]))
    if not total % 10 == int(s[-1]):
        logger.warning("CAS not valid: {} ({})".format(s, ERROR.format(s, s[-1], total % 10)))
        return None
    return s.lstrip("0")
