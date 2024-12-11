from numbers import Number
from typing import Optional

import numpy as np
from loguru import logger


def calculate_check_digit(cas: str) -> int:
    return sum((a + 1) * int(b) for a, b in zip(range(9), cas[-1::-1])) % 10


def validate_cas_string(cas: Optional[str]) -> Optional[str]:
    if isinstance(cas, str):
        cas = cas.strip()
    if not cas:
        return None
    elif isinstance(cas, Number) and np.isnan(cas):
        return None

    if "-" not in cas:
        first, second, check_digit = cas[:-3], cas[-3:-1], int(cas[-1])
        if str(calculate_check_digit(first + second)) != str(check_digit):
            logger.warning(
                "Removing invalid CAS number {}; last digit should be {}".format(
                    cas, check_digit
                )
            )
            return None
        return "-".join([first, second, str(check_digit)]).lstrip("0")
    elif cas.count("-") == 2 and not cas.split("-")[2]:
        # e.g. 1228284-64-
        check_digit = str(calculate_check_digit(cas.replace("-", "")))
        logger.warning(
            "Adding missing CAS check digit, {} -> {}".format(cas, cas + check_digit)
        )
        return cas + check_digit
    elif cas.count("-") == 2:
        first, second, third = cas.split("-")
        check_digit = calculate_check_digit(first + second)
        if str(check_digit) != third:
            logger.warning(
                "Removing invalid CAS number {}; last digit should be {}".format(
                    cas, check_digit
                )
            )
        else:
            return cas.lstrip("0")
    else:
        logger.warning(
            "Given CAS can't be validated, wrong number of hyphens are present: {}".format(
                cas
            )
        )
        return None
