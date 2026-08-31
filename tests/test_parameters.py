import pytest

from bw_simapro_csv.parameters import (
    FormulaSubstitutor,
    compile_iff_re,
    fix_iff_formula,
    fix_leading_zero_formula,
    substitute_in_formulas,
)
from bw_simapro_csv.utils import normalize_number_in_formula


def test_iff_formula_with_equals_sign():
    pattern = compile_iff_re({"decimal_separator": ","})
    given = "Iff(m=1; 1; 0)"
    expected = "((1) if (m==1) else (0))"
    assert fix_iff_formula(given, pattern) == expected


def test_iff_formula_after_normalize_number_in_formula():
    pattern = compile_iff_re({"decimal_separator": "."})
    given = "iff(A=0,1,0)"
    expected = "((1) if (A==0) else (0))"
    assert fix_iff_formula(normalize_number_in_formula(given, "."), pattern) == expected

    given = "iff(A=0, 1, 0)"
    expected = "((1) if (A==0) else (0))"
    assert fix_iff_formula(normalize_number_in_formula(given, "."), pattern) == expected

    pattern = compile_iff_re({"decimal_separator": ","})
    given = "iff(A=0,2;1,2;0)"
    expected = "((1.2) if (A==0.2) else (0))"
    assert fix_iff_formula(normalize_number_in_formula(given, ","), pattern) == expected

    given = "iff(A=0,1;1,2;0)"
    expected = "((1.2) if (A==0.1) else (0))"
    assert fix_iff_formula(normalize_number_in_formula(given, ","), pattern) == expected


def test_leading_zero_formula():
    given = [
        "01234",
        "+01234",
        "-01234",
        "0.1234",
        "01.234",
        " 01.234",
        "\t01.234",
        "1.023",
        "01.023",
        "no01",
        "e023",
        "123e023",
        "123E023",
        "123EE023",
        "123e23",
        "123*0123",
        "123*123",
        "123**0123",
        "123**123",
        "123/0123",
        "123//0123",
        "clive012",
        "clive 012",
    ]
    expected = [
        "1234",
        "+1234",
        "-1234",
        "0.1234",
        "1.234",
        " 1.234",
        "\t1.234",
        "1.023",
        "1.023",
        "no01",
        "e023",
        "123e23",
        "123E23",
        "123EE023",
        "123e23",
        "123*123",
        "123*123",
        "123**123",
        "123**123",
        "123/123",
        "123//123",
        "clive012",
        "clive 12",
    ]
    assert len(given) == len(expected)
    for g, e in zip(given, expected):
        assert fix_leading_zero_formula(g) == e
    for g, e in zip(given, expected):
        assert fix_leading_zero_formula("foo " + g) == "foo " + e


def test_substitute_in_formulas_syntax_error_has_detail():
    given = {"name": "some product", "allocation_formula": "100%"}

    with pytest.raises(SyntaxError) as excinfo:
        substitute_in_formulas(given, FormulaSubstitutor({}), "allocation_formula")

    message = str(excinfo.value)
    assert "allocation_formula" in message
    assert "100%" in message
    assert "some product" in message
    assert isinstance(excinfo.value.__cause__, SyntaxError)
