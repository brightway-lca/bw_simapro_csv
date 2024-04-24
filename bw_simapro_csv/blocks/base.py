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
    def undefined_distribution(self, amount: float) -> dict:
        return {
            "uncertainty type": UndefinedUncertainty.id,
            "loc": amount,
            "amount": amount,
        }

    def distribution(
        self, amount: str, kind: str, field1: str, field2: str, field3: str, header: dict
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
    Amount: {amount}
    Field1: {field1}
    Field2: {field2}
    Field3: {field3}
    """
            ) from exc

        if kind == "Undefined":
            return self.undefined_distribution(amount)
        if kind == "Lognormal":
            if not amount or field1 <= 0:
                logger.info("Invalid lognormal distribution: {amount}|{field1}")
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
                logger.info("Invalid normal distribution: {amount}|{field1}")
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
                logger.info("Invalid triangular distribution: {amount}|{field2}|{field3}")
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
                logger.info("Invalid uniform distribution: {amount}|{field2}|{field3}")
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
