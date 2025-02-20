import ast
import re
from copy import deepcopy
from typing import Iterable, Pattern, Type

from asteval.astutils import NameFinder
from astunparse import unparse
from loguru import logger


def add_prefix_to_uppercase_input_parameters(block: list, prefix: str = "SP_") -> list:
    """For each input parameter, uppercase and add `prefix` to its name and store the original.

    Example usage:

    ... code-block:: python

        >>> add_prefix_to_input_parameters([{'name': 'foo'}])
        [{'name': 'SP_FOO', 'original_name': 'foo'}]

    """
    for dct in block:
        dct["original_name"] = dct["name"]
        dct["name"] = f"{prefix}{dct['name']}".upper()
    return block


def build_substitutes(
    project_parameters: Iterable, database_parameters: Iterable
) -> dict[str, str]:
    """Build a dictionary of parameter name substitutions.

    Project parameters take precedence over database parameters.

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
    return {o["original_name"].upper(): o["name"] for o in database_parameters} | {
        o["original_name"].upper(): o["name"] for o in project_parameters
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


# Compile a regular expression for numbers which start with `0` (not allowed in Python).
LEADING_ZERO_RE = re.compile(
    r"(?P<prefix>^"  # Start searching at beginning of line
    + r"|[\s"  # Or preceded by white space
    + r"\+\-\*\/]"  # Or mathematical operators
    + r"|(\d[eE]))"  # Or 'e|E' for exponent (when in a number)
    + r"(?P<number>0\d)"  # The number with leading zero
)


def fix_leading_zero_formula(formula: str, pattern: Pattern = LEADING_ZERO_RE) -> str:
    """
    Replace leading zeros in numbers, as these cause Python syntax errors.

    https://github.com/brightway-lca/bw_simapro_csv/issues/19

    Parameters
    ----------
    formula : str
        A string, possibly containing leading zeros.
    pattern : compiled regular expression

    Returns
    -------
    string : str
        A string with leading zeros removed.

    Examples
    --------
    >>> string = "01.23 foo +0123 1.02 john012 123e023 123**023 123*0123 123/0123 clive012"
    >>> fix_leading_zero_formula(string)
    "1.23 foo +123 1.02 john012 123e23 123**23 123*123 123/123 clive012"
    """
    while pattern.findall(formula):
        match = next(pattern.finditer(formula))
        fixed = match.groupdict()["prefix"] + match.groupdict()["number"][1:]
        formula = formula[: match.start()] + fixed + formula[match.end() :]
    return formula


def prepare_formulas(block: list[dict], header: dict, formula_field: str = "formula") -> list[dict]:
    """Make necessary conversions so formulas can be parsed by Python.

    Does the following:

    * Substitute `^` with `**`.
    * Replace `Iff()` clauses using `fix_iff_formula()`

    """
    iff_re = compile_iff_re(header)

    for obj in block:
        # TBD: Would be better to abstract out each modification to a function and loop them
        if formula_field in obj:
            original, working = deepcopy(obj[formula_field]), obj[formula_field]
            if "^" in working:
                working = working.replace("^", "**")
                if working != original:
                    logger.debug(
                        f"""Replacing `^` in formula on line {obj['line_no']}:
            {original} >>> {working}"""
                    )

            if "yield" in working:
                fixed = working.replace("yield", "YIELD")
                logger.debug(
                    f"""Replacing `yield` statement with `YIELD` in formula on line {obj['line_no']}:
        {working} >>> {fixed}"""
                )
                working = fixed

            fixed = fix_leading_zero_formula(working)
            if fixed != working:
                logger.debug(
                    f"""Replacing leading zeros in formula on line {obj['line_no']}:
        {working} >>> {fixed}"""
                )
                working = fixed

            fixed = fix_iff_formula(working, iff_re)
            if fixed != working:
                logger.debug(
                    f"""Replacing `Iff` expression in formula on line {obj['line_no']}:
        {working} >>> {fixed}"""
                )
                working = fixed

            if working != original:
                if f"original_{formula_field}" not in obj:
                    obj[f"original_{formula_field}"] = original
            obj[formula_field] = working

    return block


class OnlySelectedUppercase(NameFinder):
    """Change name of all symbols already redefined in ``substitutes``."""

    def __init__(self, substitutes=None):
        self.substitutes = substitutes
        ast.NodeVisitor.__init__(self)

    def generic_visit(self, node):
        if node.__class__.__name__ == "Name" and node.ctx.__class__ == ast.Load:
            node.id = node.id.upper()
            try:
                node.id = self.substitutes[node.id]
            except KeyError:
                pass
        ast.NodeVisitor.generic_visit(self, node)


class FormulaSubstitutor:
    """Callable class that will substitute symbol names using ``substitutions`` substitution dictionary."""

    def __init__(self, substitutions):
        self.visitor = OnlySelectedUppercase(substitutions)

    def __call__(self, formula):
        parsed = ast.parse(formula)
        self.visitor.visit(parsed)
        return unparse(parsed).strip()


def substitute_in_formulas(obj: dict, visitor: Type, formula_field: str = "formula") -> dict:
    """Substitute variable names in `obj[formula_field]` based on `substitutions`.

    Keeps `original_formula`.

    Example usage:

    ... code-block:: python

        >>> given = {'formula': 'a * 2'}
        >>> substitutions = {'a': 'hi_mom'}
        >>> substitute_in_formulas(given, substitutions)
        {'formula': 'hi_mom * 2', 'original_formula': 'a * 2'}

    """
    if formula_field in obj:
        obj[f"original_{formula_field}"] = obj[formula_field]
        try:
            obj[formula_field] = visitor(obj[formula_field])
        except SyntaxError as exc:
            logger.critical("Syntax error in field {ff} in object {o}", ff=formula_field, o=obj)
            raise SyntaxError from exc

        if obj[f"original_{formula_field}"] == obj[formula_field]:
            del obj[f"original_{formula_field}"]

    return obj
