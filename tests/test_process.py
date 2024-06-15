import pytest

from bw_simapro_csv.blocks import GenericBiosphere, Process
from bw_simapro_csv.errors import WasteModelMismatch


def test_supplement_biosphere_edges():
    class O:
        pass

    class P(Process):
        def __init__(self):
            pass

    class B(GenericBiosphere):
        def __init__(self):
            pass

    o = O()
    o.category = "Emissions to air"
    o.parsed = [
        {"name": "first", "data": "yes please"},
        {"name": "second", "unit": "something", "comment": "already here"},
        {
            "name": "third",
            "lonely": True,
        },
    ]

    p = P()
    p.blocks = {"Emissions to air": o}

    b = B()
    b.category = "Airborne emissions"
    b.parsed = [
        {"name": "first", "cas_number": True},
        {"name": "second", "comment": "this"},
        {"name": "third", "comment": "hi mom"},
    ]

    expected = [
        {
            "name": "first",
            "data": "yes please",
            "cas_number": True,
        },
        {"name": "second", "unit": "something", "comment": "already here ⧺ this"},
        {
            "name": "third",
            "lonely": True,
            "comment": "hi mom",
        },
    ]

    p.supplement_biosphere_edges([b])
    assert p.blocks["Emissions to air"].parsed == expected


def test_check_waste_production_model_consistency_products():
    class O:
        pass

    class P(Process):
        def __init__(self):
            pass

    wt = O()
    wt.category = "Waste treatment"
    wt.parsed = [1]

    pr = O()
    pr.category = "Products"
    pr.parsed = []

    p = P()
    p.blocks = {"Products": pr, "Waste treatment": wt}
    p.parsed = {"metadata": {"Category type": "waste treatment"}}
    assert p.check_waste_production_model_consistency() is None

    wt.parsed = [1, 2, 3]
    pr.parsed = [2, 3, 4, 5]

    with pytest.raises(WasteModelMismatch) as exc_info:
        p.check_waste_production_model_consistency()

    assert "3 waste treatment inputs and 4 products" in str(exc_info.value)


def test_check_waste_production_model_consistency_category_type():
    class O:
        pass

    class P(Process):
        def __init__(self):
            pass

    wt = O()
    wt.category = "Waste treatment"
    wt.parsed = [1]

    p = P()
    p.blocks = {"Waste treatment": wt}
    p.parsed = {"metadata": {"Category type": "waste treatment"}}
    assert p.check_waste_production_model_consistency() is None

    p.parsed = {"metadata": {"Category type": "w00t"}}

    with pytest.raises(WasteModelMismatch) as exc_info:
        p.check_waste_production_model_consistency()

    assert "`waste treatment`; instead got `w00t`" in str(exc_info.value)

    pr = O()
    pr.category = "Products"
    pr.parsed = [1]

    wt.parsed = []

    p.blocks = {"Waste treatment": wt, "Products": pr}
    p.parsed = {"metadata": {"Category type": "waste treatment"}}
    with pytest.raises(WasteModelMismatch) as exc_info:
        p.check_waste_production_model_consistency()

    assert "Expected processes with `Products` blocks" in str(exc_info.value)
