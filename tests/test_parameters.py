from bw_simapro_csv.parameters import compile_iff_re, fix_iff_formula


def test_iff_formula_with_equals_sign():
    pattern = compile_iff_re({"decimal_separator": ","})
    given = "Iff(m=1; 1; 0)"
    expected = "((1) if (m==1) else (0))"
    assert fix_iff_formula(given, pattern) == expected
