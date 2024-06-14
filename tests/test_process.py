from bw_simapro_csv.blocks import GenericBiosphere, Process


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
