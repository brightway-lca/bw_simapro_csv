import pytest

from bw_simapro_csv.utils import BeKindRewind


def test_rewindable_generator():
    a = iter((1, 2, 3, 4, 5))
    r = BeKindRewind(a)
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
    r = BeKindRewind(a)
    assert next(r) == 1
    r.rewind()
    r.rewind()
    r.rewind()
    assert next(r) == 1
    assert next(r) == 2


def test_rewindable_generator_rewind_before_iteration():
    a = iter((1, 2, 3, 4, 5))
    r = BeKindRewind(a)
    r.rewind()
    assert next(r) == 1
    assert next(r) == 2


def test_rewindable_generator_strip():
    a = iter([(" a ", "\tb ", "c"), (" 2", "1 ", "3")])
    r = BeKindRewind(a, strip=True)
    assert next(r) == ["a", "b", "c"]
    assert next(r) == ["2", "1", "3"]
