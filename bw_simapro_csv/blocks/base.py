# pylint: disable=too-many-arguments,unused-argument,too-many-return-statements
import math

from loguru import logger
from stats_arrays import (
    LognormalUncertainty,
    NormalUncertainty,
    TriangularUncertainty,
    UndefinedUncertainty,
    UniformUncertainty,
)

from ..utils import asnumber


class SimaProCSVBlock:
    """Base class for parsing and cleaning logical blocks in a SimaPro CSV file"""


class EmptyBlock(SimaProCSVBlock):
    """An empty block without content."""


class SimaProCSVUncertainBlock(SimaProCSVBlock):
    """Base class which includes logic for parsing lines with probability distributions"""

    def undefined_distribution(self, amount: float) -> dict:
        return {
            "uncertainty type": UndefinedUncertainty.id,
            "loc": amount,
            "amount": amount,
        }

    def distribution(
        self,
        amount: str,
        kind: str,
        field1: str,
        field2: str,
        field3: str,
        header: dict,
        line_no: int,
        **kwargs,
    ) -> dict:
        decimal_separator = header.get("decimal_separator", ".")

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
            return self.undefined_distribution(amount)
        if kind == "Lognormal":
            if not amount or field1 <= 0:
                logger.warning(
                    f"Invalid lognormal distribution on line {line_no}: {amount}|{field1}"
                )
                return self.undefined_distribution(amount)
            return {
                "uncertainty type": LognormalUncertainty.id,
                "scale": math.log(math.sqrt(field1)),
                "loc": math.log(abs(amount)),
                "negative": amount < 0,
                "amount": amount,
            }
        if kind == "Normal":
            if not amount or field1 <= 0:
                logger.warning(f"Invalid normal distribution on line {line_no}: {amount}|{field1}")
                return self.undefined_distribution(amount)
            return {
                "uncertainty type": NormalUncertainty.id,
                "scale": math.sqrt(field1),
                "loc": amount,
                "negative": amount < 0,
                "amount": amount,
            }
        if kind == "Triangle":
            if not field2 <= amount <= field3:
                logger.warning(
                    f"Invalid triangular distribution on line {line_no}: {amount}|{field2}|{field3}"
                )
                return self.undefined_distribution(amount)
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
                logger.warning(
                    f"Invalid uniform distribution on line {line_no}: {amount}|{field2}|{field3}"
                )
                return self.undefined_distribution(amount)
            return {
                "uncertainty type": UniformUncertainty.id,
                "minimum": field2,
                "maximum": field3,
                "loc": amount,
                "negative": amount < 0,
                "amount": amount,
            }
        raise ValueError(f"Unknown uncertainty type: {kind}")
