import math

import pytest

from bw_simapro_csv.utils import (
    BeKindRewind,
    asnumber,
    clean,
    get_key_multiline_values,
    get_numbers_re,
    is_unit_first,
    jump_to_nonempty,
    normalize_number_in_formula,
    skip_empty,
)


def test_rewindable_generator():
    a = iter((1, 2, 3, 4, 5))
    r = BeKindRewind(a, clean_elements=False)
    assert next(r) == 1
    assert next(r) == 2
    assert next(r) == 3
    r.rewind()
    assert next(r) == 3
    assert next(r) == 4
    assert next(r) == 5
    with pytest.raises(StopIteration):
        next(r)


def test_rewindable_generator_idempotent():
    a = iter((1, 2, 3, 4, 5))
    r = BeKindRewind(a, clean_elements=False)
    assert next(r) == 1
    r.rewind()
    r.rewind()
    r.rewind()
    assert next(r) == 1
    assert next(r) == 2


def test_rewindable_generator_rewind_before_iteration():
    a = iter((1, 2, 3, 4, 5))
    r = BeKindRewind(a, clean_elements=False)
    r.rewind()
    assert next(r) == 1
    assert next(r) == 2


def test_rewindable_generator_strip():
    a = iter([(" a ", "\tb ", "c"), (" 2", "1 ", "3")])
    r = BeKindRewind(a)
    assert next(r) == ["a", "b", "c"]
    assert next(r) == ["2", "1", "3"]


def test_asnumber():
    assert asnumber("4.2", ".") == 4.2
    assert asnumber("400_404.2", ".") == 400404.2
    assert asnumber("400_404;2", ";") == 400404.2
    assert asnumber("400.404,2", ",") == 400404.2


def test_asnumber_percentage():
    assert math.isclose(asnumber("400.404,2%", ","), 4004.042)


def test_asnumber_allow_nonnumber():
    assert asnumber("foo", allow_nonnumber=True) == "foo"


def test_asnumber_error():
    with pytest.raises(ValueError):
        asnumber("foo")


def test_clean():
    assert clean("Ã¯Â¾Âµg") == "ï¾µg"
    assert clean("  \t foo") == "foo"
    assert clean("  \t foo") == "foo"
    assert clean("Â\x8dg") == "Âg"
    assert clean("CO2\x1a") == "CO2"
    assert clean("CO2") == "CO\n2"


def test_normalize_number_in_formula():
    assert normalize_number_in_formula("400_404;2", ";") == "400404.2"
    assert normalize_number_in_formula("400_404?2", "?") == "400404.2"
    assert normalize_number_in_formula("400,404.2", ".") == "400404.2"
    assert normalize_number_in_formula("400.404,2", ",") == "400404.2"
    assert normalize_number_in_formula("alpha * 400.404,2", ",") == "alpha * 400404.2"
    assert normalize_number_in_formula("alpha * 400.404*2", "*") == "alpha * 400404.2"


def test_is_number_first_decimal():
    re = get_numbers_re(".")
    assert re.match("0.000623954323")
    assert not re.match("m3")
    assert is_unit_first("m3", "0.000623954323", re) is True
    assert is_unit_first("0.000623954323", "m3", re) is False
    assert is_unit_first("MJ", "m3", re) is None


def test_is_number_first_comma():
    re = get_numbers_re(",")
    assert re.match("0,00062_39543.23")
    assert not re.match("m3")
    assert is_unit_first("m3", "0,000623954323", re) is True
    assert is_unit_first("0,000623954323", "m3", re) is False
    assert is_unit_first("MJ", "m3", re) is None


def test_is_number_first_semicolon():
    re = get_numbers_re(";")
    assert re.match("0;000623_954323")
    assert not re.match("m3")
    assert is_unit_first("m3", "0;000623954323", re) is True
    assert is_unit_first("0;000623954323", "m3", re) is False
    assert is_unit_first("MJ", "m3", re) is None


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
