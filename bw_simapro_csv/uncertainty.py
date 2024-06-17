import math

from loguru import logger
from stats_arrays import (
    LognormalUncertainty,
    NormalUncertainty,
    NoUncertainty,
    TriangularUncertainty,
    UndefinedUncertainty,
    UniformUncertainty,
)

from .utils import asnumber


def undefined_distribution(amount: float) -> dict:
    return {
        "uncertainty type": UndefinedUncertainty.id,
        "loc": amount,
        "amount": amount,
    }


def clean_simapro_uncertainty_fields(obj: dict) -> dict:
    """Remove SimaPro uncertainty field once a valid distribution has been created."""
    if "uncertainty type" not in obj:
        raise ValueError("This data object doesn't have an uncertainty distribution")
    for field in ("kind", "field1", "field2", "field3"):
        if field in obj:
            del obj[field]
    return obj


def distribution(
    amount: str,
    kind: str,
    field1: str,
    field2: str,
    field3: str,
    decimal_separator: str,
    line_no: int,
    **kwargs,
) -> dict:
    """Convert SimaPro uncertainty fields into a form suitable for `stats_arrays`, and correct
    common errors."""
    try:
        amount = asnumber(value=amount, decimal_separator=decimal_separator)
        field1 = asnumber(value=field1, decimal_separator=decimal_separator)
        field2 = asnumber(value=field2, decimal_separator=decimal_separator)
        field3 = asnumber(value=field3, decimal_separator=decimal_separator)
    except ValueError as exc:
        raise ValueError(
            f"""
Can't convert uncertainty data to numbers:
Uncertainty type: {kind}
Amount: {amount}
Field1: {field1}
Field2: {field2}
Field3: {field3}
Line number: {line_no}
"""
        ) from exc

    if kind == "Undefined":
        return undefined_distribution(amount)
    if kind == "Lognormal":
        if not amount or field1 <= 0:
            logger.debug(f"Invalid lognormal distribution on line {line_no}: {amount}|{field1}")
            return undefined_distribution(amount)
        return {
            "uncertainty type": LognormalUncertainty.id,
            "scale": math.log(math.sqrt(field1)),
            "loc": math.log(abs(amount)),
            "negative": amount < 0,
            "amount": amount,
        }
    if kind == "Normal":
        if field1 <= 0:
            logger.debug(f"Invalid normal distribution (sigma <= 0) on line {line_no}: {field1}")
            return undefined_distribution(amount)
        return {
            "uncertainty type": NormalUncertainty.id,
            "scale": math.sqrt(field1),
            "loc": amount,
            "negative": amount < 0,
            "amount": amount,
        }
    if kind == "Triangle":
        if not field2 <= amount <= field3:
            logger.debug(
                f"Invalid triangular distribution on line {line_no}: {amount}|{field2}|{field3}"
            )
            return undefined_distribution(amount)
        return {
            "uncertainty type": TriangularUncertainty.id,
            "minimum": field2,
            "maximum": field3,
            "loc": amount,
            "negative": amount < 0,
            "amount": amount,
        }
    if kind == "Uniform":
        if not field2 <= amount <= field3:
            logger.debug(
                f"Invalid uniform distribution on line {line_no}: {amount}|{field2}|{field3}"
            )
            return undefined_distribution(amount)
        return {
            "uncertainty type": UniformUncertainty.id,
            "minimum": field2,
            "maximum": field3,
            "loc": amount,
            "negative": amount < 0,
            "amount": amount,
        }
    raise ValueError(f"Unknown uncertainty type: {kind}")


def recalculate_uncertainty_distribution(dist: dict, scale: float = 1.0) -> dict:
    """Adjust uncertainty distribution to possible new `amount` value and scale."""
    if scale == 0:
        logger.warning(f"Scaling by zero removes all uncertainty: {dist}")
        return undefined_distribution(0)

    amount = dist["amount"] * scale
    if dist["uncertainty type"] in (NoUncertainty.id, UndefinedUncertainty.id):
        dist["amount"] = amount
    elif dist["uncertainty type"] == LognormalUncertainty.id:
        dist.update(
            {
                "loc": math.log(abs(amount)),
                "negative": amount < 0,
                "amount": amount,
            }
        )
    elif dist["uncertainty type"] == NormalUncertainty.id:
        dist.update(
            {
                "scale": dist["scale"] * abs(scale),
                "loc": amount,
                "negative": amount < 0,
                "amount": amount,
            }
        )
    elif dist["uncertainty type"] in (TriangularUncertainty.id, UniformUncertainty.id):
        if scale < 0:
            dist.update(
                {
                    "minimum": dist["maximum"] * scale,
                    "maximum": dist["minimum"] * scale,
                    "loc": amount,
                    "negative": amount < 0,
                    "amount": amount,
                }
            )
        else:
            dist.update(
                {
                    "minimum": dist["minimum"] * scale,
                    "maximum": dist["maximum"] * scale,
                    "loc": amount,
                    "negative": amount < 0,
                    "amount": amount,
                }
            )
    return dist
