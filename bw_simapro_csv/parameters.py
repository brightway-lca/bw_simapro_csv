import re
from typing import Iterable, Pattern

from bw2parameters import FormulaSubstitutor
from loguru import logger


def add_prefix_to_input_parameters(block: list, prefix: str = "sp_") -> list:
    """For each input parameter, add `prefix` to its name and store the original.

    Example usage:

    ... code-block:: python

        >>> add_prefix_to_input_parameters([{'name': 'foo'}])
        [{'name': 'sp_foo', 'original_name': 'foo'}]

    """
    for dct in block:
        dct["original_name"] = dct["name"]
        dct["name"] = f"{prefix}{dct['name']}"
    return block


def build_substitutes(
    project_parameters: Iterable, database_parameters: Iterable
) -> dict[str, str]:
    """Build a dictionary of parameter name substitutions.

    Database parameters take precedence over project parameters.

    Example usage:

    ... code-block:: python

        >>> p = [
        >>>         {'name': 'sp_foo', 'original_name': 'foo'},
        >>>         {'name': 'sp_bar', 'original_name': 'bar'}
        >>>     ]
        >>> d = [{'name': 'hey_foo', 'original_name': 'foo'}]
        >>> build_substitutes(p, d)
        {'foo': 'hey_foo', 'bar': 'sp_bar'}

    """
    return {o["original_name"]: o["name"] for o in project_parameters} | {
        o["original_name"]: o["name"] for o in database_parameters
    }


def compile_iff_re(header: dict) -> Pattern:
    """Compile a regular expression for `Iff` patterns taking the decimal separator into account.

    Normally a SimaPro `Iff` expression has the form `Iff(test, if_true, if_false)`; however, if
    the decimal separator is ",", then it has the form `Iff(test; if_true; if_false)`"""
    separator = ";" if header.get("decimal_separator") == "," else ","
    return re.compile(
        "iff\\("  # Starting condition, case-insensitive
        + "\\s*"  # Whitespace
        + f"(?P<condition>[^{separator}]+)"  # Anything except separator
        + "\\s*"  # Whitespace
        + separator
        + "\\s*"  # Whitespace
        + f"(?P<when_true>[^{separator}]+)"  # Value if condition is true
        + "\\s*"  # Whitespace
        + separator
        + "\\s*"  # Whitespace
        + f"(?P<when_false>[^{separator}]+)"  # Value if condition is false
        + "\\s*"  # Whitespace
        + "\\)",  # End parentheses
        re.IGNORECASE,
    )


def fix_iff_formula(formula: str, pattern: Pattern) -> str:
    """
    Replace SimaPro 'iff' formula with a Python equivalent 'if-else' expression.

    Processes a given string containing SimaPro 'iff' formulae and
    replaces them with Python equivalent 'if-else' expressions. The conversion
    is done using regular expressions.

    Parameters
    ----------
    formula : str
        A string containing SimaPro 'iff' formulae.
    pattern : compiled regular expression from `compile_iff_re`

    Returns
    -------
    string : str
        A string with SimaPro 'iff' formulae replaced by Python 'if-else' expressions.

    Examples
    --------
    >>> string = "iff(A > 0, A, 0)"
    >>> fix_iff_formula(string, compile_iff_re({}))
    "((A) if (A > 0) else (0))"
    """
    while pattern.findall(formula):
        match = next(pattern.finditer(formula))
        condition_fixed = match.groupdict()["condition"].replace("=", "==")
        formula = (
            formula[: match.start()]
            + "(({when_true}) if ({condition_fixed}) else ({when_false}))".format(
                condition_fixed=condition_fixed, **match.groupdict()
            )
            + formula[match.end() :]
        )
    return formula


def prepare_formulas(block: list[dict], header: dict) -> list[dict]:
    """Make necessary conversions so formulas can be parsed by Python.

    Does the following:

    * Substitute `^` with `**`.
    * Replace `Iff()` clauses using `fix_iff_formula()`

    """
    iff_re = compile_iff_re(header)

    for obj in block:
        if "formula" in obj:
            if "^" in obj["formula"]:
                new_formula = obj["formula"].replace("^", "**")
                logger.info(
                    f"""Replacing `^` in formula on line {obj['line_no']}:
        {obj['formula']} >>> {new_formula}"""
                )
                if "original_formula" not in obj["formula"]:
                    obj["original_formula"] = obj["formula"]
                obj["formula"] = new_formula

            new_formula = fix_iff_formula(obj["formula"], iff_re)
            if new_formula != obj["formula"]:
                logger.info(
                    f"""Replacing `Iff` expression in formula on line {obj['line_no']}:
        {obj['formula']} >>> {new_formula}"""
                )
                if "original_formula" not in obj["formula"]:
                    obj["original_formula"] = obj["formula"]
                obj["formula"] = new_formula

    return block


def substitute_in_formulas(obj: dict, substitutions: dict) -> dict:
    """Substitute variables names in `obj['formula']` based on `substitutions`.

    Keeps `original_formula`.

    Example usage:

    ... code-block:: python

        >>> given = {'formula': 'a * 2'}
        >>> substitutions = {'a': 'hi_mom'}
        >>> substitute_in_formulas(given, substitutions)
        {'formula': 'hi_mom * 2', 'original_formula': 'a * 2'}

    """
    visitor = FormulaSubstitutor(substitutions)

    if "formula" in obj:
        obj["original_formula"] = obj["formula"]
        obj["formula"] = visitor(obj["formula"])

    return obj
