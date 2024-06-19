import stats_arrays as sa

from bw_simapro_csv.blocks import GenericUncertainBiosphere, Process, Units
from bw_simapro_csv.units import normalize_units


def test_unit_normalization():
    class G(GenericUncertainBiosphere):
        def __init__(self):
            pass

    class U(Units):
        def __init__(self):
            pass

    class P(Process):
        def __init__(self):
            pass

    unit_block = U()
    unit_block.parsed = [
        {
            "name": "g",
            "reference unit name": "kg",
            "conversion": 1e-3,
            "dimension": "Mass",
            "line_no": 1,
        }
    ]

    block = G()
    block.parsed = [
        {
            "unit": "g",
            "amount": 1000,
            "formula": "foo * bar",
            "uncertainty type": sa.TriangularUncertainty.id,
            "minimum": 500,
            "maximum": 1500,
            "loc": 1000,
            "line_no": 1,
        }
    ]
    p = P()
    p.blocks = {"Emissions to soil": block}

    expected = [
        {
            "unit": "kg",
            "amount": 1.0,
            "original unit before conversion": "g",
            "unit conversion factor": 0.001,
            "formula": "(foo * bar) * 0.001",
            "negative": False,
            "uncertainty type": sa.TriangularUncertainty.id,
            "minimum": 0.5,
            "maximum": 1.5,
            "loc": 1.0,
            "line_no": 1,
        }
    ]
    normalize_units([unit_block, p])
    assert block.parsed == expected
