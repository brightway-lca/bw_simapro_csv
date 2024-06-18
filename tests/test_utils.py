import math

import pytest

from bw_simapro_csv.utils import (
    add_amount_or_formula,
    asnumber,
    get_key_multiline_values,
    get_numbers_re,
    jump_to_nonempty,
    normalize_number_in_formula,
    skip_empty,
)


def test_asnumber():
    assert asnumber("4.2", ".") == 4.2
    assert asnumber("400_404.2", ".") == 400404.2
    assert asnumber("400_404;2", ";") == 400404.2
    assert asnumber("400404,2", ",") == 400404.2


def test_asnumber_percentage():
    assert math.isclose(asnumber("400404,2%", ","), 4004.042)


def test_asnumber_allow_nonnumber():
    assert asnumber("foo", allow_nonnumber=True) == "foo"


def test_asnumber_error():
    with pytest.raises(ValueError):
        asnumber("foo")


def test_normalize_number_in_formula():
    assert normalize_number_in_formula("400404;2", ";") == "400404.2"
    assert normalize_number_in_formula("400404?2", "?") == "400404.2"
    assert normalize_number_in_formula("400404.2", ".") == "400404.2"
    assert normalize_number_in_formula("400404,2", ",") == "400404.2"
    assert normalize_number_in_formula("alpha * 400404,2", ",") == "alpha * 400404.2"
    assert normalize_number_in_formula("alpha * 400404*2", "*") == "alpha * 400404.2"
    assert normalize_number_in_formula("PM2_5", ",") == "PM2_5"
    assert normalize_number_in_formula("4,45E-4*,8/1000", ",") == "4.45E-4*.8/1000"


def test_skip_empty():
    data = [(0, ["foo"]), (1, []), (2, [None, None]), (3, ["bar"])]
    assert list(skip_empty(data)) == [(0, ["foo"]), (3, ["bar"])]


def test_jump_to_nonempty():
    data = [(0, []), (1, []), (2, [None, None]), (3, ["bar"])]
    assert jump_to_nonempty(data) == [(3, ["bar"])]


def test_get_key_multilines_value():
    given = [
        (0, []),
        (1, [""]),
        (2, ["", ""]),
        (3, [None, ""]),
        (4, ["Header"]),
        (5, [None]),
        (6, ["data", 1]),
        (7, ["data", 2]),
        (8, []),
        (9, ["Header 2"]),
        (10, [""]),
        (11, ["data", 3]),
    ]
    expected = [
        ("Header", [(6, ["data", 1]), (7, ["data", 2])]),
        ("Header 2", [(11, ["data", 3])]),
    ]
    assert list(get_key_multiline_values(given, [])) == expected


def test_get_key_multilines_value_stop_words():
    given = [
        (0, []),
        (1, [""]),
        (2, ["", ""]),
        (3, [None, ""]),
        (4, ["Header"]),
        (5, [None]),
        (6, ["data", 1]),
        (7, ["data", 2]),
        (8, []),
        (9, ["Header 2"]),
        (10, [""]),
        (11, ["Stop"]),
        (12, ["data", 3]),
    ]
    expected = [
        ("Header", [(6, ["data", 1]), (7, ["data", 2])]),
        ("Stop", [(12, ["data", 3])]),
    ]
    assert list(get_key_multiline_values(given, ["Stop"])) == expected


def test_get_key_multiline_values_error():
    given = [(0, []), (1, [""]), (2, ["Foo", "bar"]), (3, [None])]
    with pytest.raises(ValueError):
        list(get_key_multiline_values(given, []))


def test_get_key_multilines_value_stop_on_empty_block():
    given = [
        (0, []),
        (1, [""]),
        (2, ["", ""]),
        (3, [None, ""]),
        (4, ["Header"]),
        (5, [None]),
        (6, ["data", 1]),
        (7, ["data", 2]),
        (8, []),
        (9, ["Header 2"]),
        (10, [""]),
        (11, ["Stop"]),
        (12, []),
    ]
    expected = [
        ("Header", [(6, ["data", 1]), (7, ["data", 2])]),
    ]
    assert list(get_key_multiline_values(given, ["Stop"])) == expected


def test_get_numbers_re():
    assert get_numbers_re(",").match("1,11657894165076E-9")
    assert get_numbers_re(";").match("1;11657894165076E-9")
    assert get_numbers_re(".").match("1.11657894165076E-9")

    assert get_numbers_re(",").match("1,11657894165076e-9")
    assert get_numbers_re(";").match("1;11657894165076e-9")
    assert get_numbers_re(".").match("1.11657894165076e-9")

    assert get_numbers_re(",").match("1,11657894165076e9")
    assert get_numbers_re(";").match("1;11657894165076e9")
    assert get_numbers_re(".").match("1.11657894165076e9")

    assert get_numbers_re(",").match(" \t1,11657894165076E-9\n")

    assert not get_numbers_re(",").match("e1234")
    assert not get_numbers_re(",").match("259,26-2,81")


def test_add_amount_or_formula():
    assert add_amount_or_formula({}, "3.141", ".") == {"amount": 3.141}
    assert add_amount_or_formula({}, "pi", ".") == {"formula": "pi"}
    assert add_amount_or_formula({}, "259,26-2,81", ",") == {"formula": "259.26-2.81"}
    assert add_amount_or_formula({}, "259,26-2", ",") == {"formula": "259.26-2"}
    assert add_amount_or_formula({}, "1,1165E-9", ",") == {"amount": 1.1165e-9}
    assert add_amount_or_formula({}, "3,14159 * pi", ",") == {"formula": "3.14159 * pi"}
    assert add_amount_or_formula({}, "3,14159 * pi", ",", formula_key="foo") == {
        "foo": "3.14159 * pi"
    }
    assert add_amount_or_formula({}, "3;141", ";", amount_key="foo") == {"foo": 3.141}
