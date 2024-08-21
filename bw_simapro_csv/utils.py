import itertools
import re
from copy import copy
from datetime import date, datetime
from numbers import Number
from typing import Iterable, List, Pattern, Union

from bw2parameters import ParameterSet
from dateutil.parser import parse as dtparse
from loguru import logger

from .errors import FormulaReservedWord


def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, itertools.chain):
        return list(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def nobraces(s: str) -> str:
    """Remove braces from header section elements"""
    return s[s.find("{") + 1 : s.rfind("}")]


def noquotes(s: str) -> str:
    """Remove string start/end characters"""
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


def asboolean(s: str, allow_nonboolean: bool = False) -> bool:
    """Convert SimaPro strings to actual booleans"""
    if s.lower() in {"yes", "y", "true", "t", "1"}:
        return True
    if s.lower() in {"no", "n", "false", "f", "0"}:
        return False
    if allow_nonboolean:
        return s
    # Better raise an error then assume we understand SimaPro
    raise ValueError(f"Can't convert '{s}' to boolean")


comma = re.compile(",(\\d)")
period = re.compile("\\.(\\d)")
RE_SPECIAL = ".*^$+?[]\\|"


def normalize_number_in_formula(formula: str, decimal_separator: str = ".") -> str:
    if decimal_separator == ",":
        formula = comma.sub(".\\g<1>", formula)
    elif decimal_separator == ".":
        pass
    else:
        if decimal_separator in RE_SPECIAL:
            decimal_separator = f"\\{decimal_separator}"
        formula = re.sub(f"{decimal_separator}(\\d)", ".\\g<1>", formula)
    return formula


def asnumber(
    value: Union[str, Number], decimal_separator: str = ".", allow_nonnumber: bool = False
) -> Union[Number, str]:
    """Take a number stored as a string and convert to a float.

    Tries hard to handle different formats."""
    if isinstance(value, Number):
        return value

    original = copy(value)

    conversion = 1.0
    value = normalize_number_in_formula(value, decimal_separator)
    if value.endswith("%"):
        value = value.replace("%", "")
        conversion = 0.01
    try:
        return float(value) * conversion
    except ValueError as exc:
        if allow_nonnumber:
            return original
        raise ValueError from exc


def asdate(value: str, dayfirst: bool = True) -> date:
    """Parse a string to a `datetime.date`"""
    return dtparse(value, dayfirst=dayfirst).date()


def alternating_key_value(data: List[list]) -> List[tuple]:
    """Transform data in alternating key/value/blank rows to tuples with `(key, value)`.

    For example, turn:

    ```

    Foo
    bar; baz

    ```

    Into:

    ```python
    [("Foo", ["bar", "baz"])]
    ```

    """
    processed = []
    index = 0
    data = [line for _, line in data]

    if not any(data[index]):
        index += 1

    while index < len(data):
        if not len(data[index]) == 1:
            raise ValueError(f"Line {data[index]} is supposed to be single-element")
        key, value = data[index], data[index + 1]
        if not value:
            processed.append((data[index][0], None))
        elif len(value) == 1:
            processed.append((data[index][0], data[index + 1][0]))
        else:
            processed.append((data[index][0], data[index + 1]))
        index += 2

        if index < len(data) and not any(data[index]):
            index += 1

    return processed


def get_numbers_re(separator: str) -> Pattern:
    if separator == ".":
        separator = "\\."
    return re.compile(f"^\\s*[-+]?[\\d]+{separator}?[\\d]*([Ee][+-]*[0-9]+)?\\s*$")


def add_amount_or_formula(
    data: dict,
    value: str,
    decimal_separator: str,
    amount_key: str = "amount",
    formula_key: str = "formula",
) -> dict:
    """Add amount or formula depending on `value` form"""
    if get_numbers_re(decimal_separator).match(value):
        data[amount_key] = asnumber(value, decimal_separator)
    else:
        data[formula_key] = normalize_number_in_formula(value, decimal_separator)
    return data


def skip_empty(data: list) -> Iterable:
    """Return iterable of nonempty lines"""
    for x, y in data:
        if not y or not any(y):
            continue
        yield x, y


def jump_to_nonempty(data: list) -> list:
    """Skip empty rows at beginning of list"""
    for i, (x, y) in enumerate(data):
        if not y or not any(y):
            continue
        break
    return data[i:]


def get_key_multiline_values(block: list[tuple], stop_terms: Iterable) -> tuple[str, list]:
    """Pull off the first non-empty line, then optional empty lines, and then each data line until
    an empty line"""
    while block:
        block = jump_to_nonempty(block)
        if not any(data for _, data in block):
            return
        _, key = block.pop(0)
        if len(key) != 1:
            raise ValueError(f"Block header should have one element; found {len(key)}: {key}")
        key = key[0]
        block = jump_to_nonempty(block)

        data = []
        while block:
            line_no, line = block.pop(0)
            if len(line) == 1 and line[0] in stop_terms:
                block.insert(0, (line_no, line))
                break
            elif not line or not any(line):
                break
            data.append((line_no, line))
        if data:
            yield key, data


def parameter_set_evaluate_each_formula(ps: ParameterSet) -> dict[str, float]:
    """
    Do manual evaluation to catch math errors and give individual context.

    Copied from https://github.com/brightway-lca/brightway2-parameters/blob/main/bw2parameters/parameter_set.py.
    """
    result = {}
    for key in ps.order:
        if key in ps.global_params:
            value = ps.global_params[key]
        elif ps.params[key].get("formula"):
            try:
                value = ps.interpreter(ps.params[key]["formula"])
            except ZeroDivisionError:
                logger.critical(
                    f"""
    Division by zero in formula {ps.params[key]['formula']} on line {ps.params[key]['line_no']}.
    Returning zero, and moving `formula` to `invalid_formula`.
                """
                )
                value = 0
                ps.params[key]["invalid_formula"] = ps.params[key]["formula"]
                del ps.params[key]["formula"]
            except NotImplementedError as exc:
                raise FormulaReservedWord(
                    f"""
    Given formula {ps.params[key]['formula']} uses a Python reserved token.
    Please report this at https://github.com/brightway-lca/bw_simapro_csv/issues
    We can add it to the cleaning step.
                """
                ) from exc
        elif "amount" in ps.params[key]:
            value = ps.params[key]["amount"]
        else:
            raise ValueError("No suitable formula or static amount found " "in {}".format(key))
        result[key] = value
        ps.interpreter.add_symbols({key: value})

    for key, value in ps.params.items():
        value["amount"] = result[key]
    return result
