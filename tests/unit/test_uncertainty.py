import math

import pytest
from stats_arrays import (
    LognormalUncertainty,
    NormalUncertainty,
    TriangularUncertainty,
    UndefinedUncertainty,
    UniformUncertainty,
)

from bw_simapro_csv.uncertainty import clean_simapro_uncertainty_fields, distribution


def test_clean_simapro_uncertainty_fields():
    given = {"field1": "foo", "kind": "bar", "uncertainty type": LognormalUncertainty.id}
    assert clean_simapro_uncertainty_fields(given) == {"uncertainty type": LognormalUncertainty.id}


def test_distribution_nonnumbers():
    given = {
        "amount": "",
        "kind": "Lognormal",
        "field1": "4",
        "field2": "0",
        "field3": "0",
        "decimal_separator": ".",
        "line_no": 7,
    }
    with pytest.raises(ValueError):
        distribution(**given)
    given["amount"] = "zero"
    with pytest.raises(ValueError):
        distribution(**given)


def test_distribution_lognormal_valid():
    # SimaPro inputs follow previous ecoinvent formats and are:
    # amount - geometric mean
    # field1 - e ^ (sigma ^ 2)
    expected = {
        "uncertainty type": LognormalUncertainty.id,
        "scale": math.log(2),
        "loc": 0.0,
        "amount": 1.0,
        "negative": False,
    }
    given = {
        "amount": "1",
        "kind": "Lognormal",
        "field1": "4",
        "field2": "0",
        "field3": "0",
        "decimal_separator": ".",
        "line_no": 7,
    }
    assert distribution(**given) == expected


def test_distribution_lognormal_valid_negative():
    expected = {
        "uncertainty type": LognormalUncertainty.id,
        "scale": math.log(2),
        "loc": 0.0,
        "amount": -1.0,
        "negative": True,
    }
    given = {
        "amount": "-1",
        "kind": "Lognormal",
        "field1": "4",
        "field2": "0",
        "field3": "0",
        "decimal_separator": ".",
        "line_no": 7,
    }
    assert distribution(**given) == expected


def test_distribution_lognormal_invalid_0_mu():
    expected = {
        "uncertainty type": UndefinedUncertainty.id,
        "loc": 0.0,
        "amount": 0.0,
    }
    given = {
        "amount": "0",
        "kind": "Lognormal",
        "field1": "4",
        "field2": "0",
        "field3": "0",
        "decimal_separator": ".",
        "line_no": 7,
    }
    assert distribution(**given) == expected


def test_distribution_lognormal_invalid_0_sigma():
    expected = {
        "uncertainty type": UndefinedUncertainty.id,
        "loc": 1.0,
        "amount": 1.0,
    }
    given = {
        "amount": "1",
        "kind": "Lognormal",
        "field1": "1",
        "field2": "0",
        "field3": "0",
        "decimal_separator": ".",
        "line_no": 7,
    }
    assert distribution(**given) == expected


def test_distribution_normal_valid():
    # SimaPro inputs follow previous ecoinvent formats and are:
    # amount - mean
    # field1 - sigma ^ 2
    expected = {
        "uncertainty type": NormalUncertainty.id,
        "scale": 2.0,
        "loc": 1.0,
        "amount": 1.0,
        "negative": False,
    }
    given = {
        "amount": "1",
        "kind": "Normal",
        "field1": "4",
        "field2": "0",
        "field3": "0",
        "decimal_separator": ".",
        "line_no": 7,
    }
    assert distribution(**given) == expected


def test_distribution_normal_valid_negative():
    # SimaPro inputs follow previous ecoinvent formats and are:
    # amount - mean
    # field1 - sigma ^ 2
    expected = {
        "uncertainty type": NormalUncertainty.id,
        "scale": 2.0,
        "loc": -1.0,
        "amount": -1.0,
        "negative": True,
    }
    given = {
        "amount": "-1",
        "kind": "Normal",
        "field1": "4",
        "field2": "0",
        "field3": "0",
        "decimal_separator": ".",
        "line_no": 7,
    }
    assert distribution(**given) == expected


def test_distribution_normal_valid_zero():
    # SimaPro inputs follow previous ecoinvent formats and are:
    # amount - mean
    # field1 - sigma ^ 2
    expected = {
        "uncertainty type": NormalUncertainty.id,
        "scale": 2.0,
        "loc": 0.0,
        "amount": 0.0,
        "negative": False,
    }
    given = {
        "amount": "0",
        "kind": "Normal",
        "field1": "4",
        "field2": "0",
        "field3": "0",
        "decimal_separator": ".",
        "line_no": 7,
    }
    assert distribution(**given) == expected


def test_distribution_normal_invalid_0_sigma():
    expected = {
        "uncertainty type": UndefinedUncertainty.id,
        "loc": 0.0,
        "amount": 0.0,
    }
    given = {
        "amount": "0",
        "kind": "Lognormal",
        "field1": "0",
        "field2": "0",
        "field3": "0",
        "decimal_separator": ".",
        "line_no": 7,
    }
    assert distribution(**given) == expected


def test_distribution_triangular_valid():
    expected = {
        "uncertainty type": TriangularUncertainty.id,
        "minimum": 1.0,
        "maximum": 3.0,
        "loc": 2.0,
        "amount": 2.0,
        "negative": False,
    }
    given = {
        "amount": "2",
        "kind": "Triangle",
        "field1": "0",
        "field2": "1",
        "field3": "3",
        "decimal_separator": ".",
        "line_no": 7,
    }
    assert distribution(**given) == expected


def test_distribution_triangular_invalid_bounds_flipped():
    expected = {
        "uncertainty type": UndefinedUncertainty.id,
        "loc": 2.0,
        "amount": 2.0,
    }
    given = {
        "amount": "2",
        "kind": "Triangle",
        "field1": "0",
        "field2": "3",
        "field3": "1",
        "decimal_separator": ".",
        "line_no": 7,
    }
    assert distribution(**given) == expected


def test_distribution_triangular_invalid_all_same():
    expected = {
        "uncertainty type": UndefinedUncertainty.id,
        "loc": 1.0,
        "amount": 1.0,
    }
    given = {
        "amount": "1",
        "kind": "Triangle",
        "field1": "0",
        "field2": "1",
        "field3": "1",
        "decimal_separator": ".",
        "line_no": 7,
    }
    assert distribution(**given) == expected


def test_distribution_triangular_invalid_mean_outside_bounds():
    expected = {
        "uncertainty type": UndefinedUncertainty.id,
        "loc": 2.0,
        "amount": 2.0,
    }
    given = {
        "amount": "2",
        "kind": "Triangle",
        "field1": "0",
        "field2": "10",
        "field3": "30",
        "decimal_separator": ".",
        "line_no": 7,
    }
    assert distribution(**given) == expected


def test_distribution_uniform_valid():
    expected = {
        "uncertainty type": UniformUncertainty.id,
        "minimum": 1.0,
        "maximum": 3.0,
        "loc": 2.0,
        "amount": 2.0,
        "negative": False,
    }
    given = {
        "amount": "2",
        "kind": "Uniform",
        "field1": "0",
        "field2": "1",
        "field3": "3",
        "decimal_separator": ".",
        "line_no": 7,
    }
    assert distribution(**given) == expected


def test_distribution_uniform_invalid_bounds_flipped():
    expected = {
        "uncertainty type": UndefinedUncertainty.id,
        "loc": 2.0,
        "amount": 2.0,
    }
    given = {
        "amount": "2",
        "kind": "Uniform",
        "field1": "0",
        "field2": "3",
        "field3": "1",
        "decimal_separator": ".",
        "line_no": 7,
    }
    assert distribution(**given) == expected


def test_distribution_uniform_invalid_all_same():
    expected = {
        "uncertainty type": UndefinedUncertainty.id,
        "loc": 1.0,
        "amount": 1.0,
    }
    given = {
        "amount": "1",
        "kind": "Uniform",
        "field1": "0",
        "field2": "1",
        "field3": "1",
        "decimal_separator": ".",
        "line_no": 7,
    }
    assert distribution(**given) == expected


def test_distribution_uniform_invalid_mean_outside_bounds():
    expected = {
        "uncertainty type": UndefinedUncertainty.id,
        "loc": 2.0,
        "amount": 2.0,
    }
    given = {
        "amount": "2",
        "kind": "Uniform",
        "field1": "0",
        "field2": "10",
        "field3": "30",
        "decimal_separator": ".",
        "line_no": 7,
    }
    assert distribution(**given) == expected


def test_distribution_unknown_distribution():
    given = {
        "amount": "2",
        "kind": "Weird",
        "field1": "1",
        "field2": "2",
        "field3": "3",
        "decimal_separator": ".",
        "line_no": 7,
    }
    with pytest.raises(ValueError):
        distribution(**given)
