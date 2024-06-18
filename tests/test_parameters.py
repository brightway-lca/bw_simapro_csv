from bw_simapro_csv.parameters import compile_iff_re, fix_iff_formula
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
