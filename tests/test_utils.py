import math

import pytest

from bw_simapro_csv.utils import BeKindRewind, asnumber, clean, normalize_number_in_formula


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
