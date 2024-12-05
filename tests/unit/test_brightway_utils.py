from bw_simapro_csv.blocks import Process
from bw_simapro_csv.brightway import name_for_process


def test_name_for_process_given_name():
    class P(Process):
        def __init__(self):
            pass

    p = P()
    p.parsed = {"metadata": {"Process name": "foo"}}

    assert name_for_process(p, "bar") == "foo"


def test_name_for_process_given_name_unspecified():
    class P(Process):
        def __init__(self):
            pass

    p = P()
    p.blocks = {}
    p.parsed = {"metadata": {"Process name": "unspecified"}}
    assert name_for_process(p, "bar") == "bar"

    p.parsed = {"metadata": {"Process name": "UNSPECIFIED"}}
    assert name_for_process(p, "bar") == "bar"


def test_name_for_process_products():
    class Dummy:
        pass

    class P(Process):
        def __init__(self):
            pass

    o = Dummy()
    o.parsed = [{"name": "foo"}, {"name": "bar"}]

    p = P()
    p.blocks = {"Products": o}
    p.parsed = {"metadata": {}}

    assert name_for_process(p, "no") == "MFP: foo⧺bar"


def test_name_for_process_products_clean_name():
    class Dummy:
        pass

    class P(Process):
        def __init__(self):
            pass

    o = Dummy()
    o.parsed = [
        {"name": r"Albacore, fillet, raw, at processing {FR} U"},
        {"name": r"Albacore, residues, raw, at processing {FR} U"},
    ]

    p = P()
    p.blocks = {"Waste treatment": o}
    p.parsed = {"metadata": {}}

    assert name_for_process(p, "no") == "MFP: Albacore, fillet, raw, at⧺Albacore, residues, raw"


def test_name_for_process_products_shorten_name():
    class Dummy:
        pass

    class P(Process):
        def __init__(self):
            pass

    o = Dummy()
    o.parsed = [
        {"name": r"Albacore, fillet, raw, at processing {FR} U"},
        {"name": r"Albacore, residues, raw, at processing {FR} U"},
    ]

    p = P()
    p.blocks = {"Waste treatment": o}
    p.parsed = {"metadata": {}}

    assert (
        name_for_process(p, "no", shorten_names=False)
        == r"MFP: Albacore, fillet, raw, at processing {FR} U⧺Albacore, residues, raw, at processing {FR} U"
    )


def test_name_for_waste_treatment_products():
    class Dummy:
        pass

    class P(Process):
        def __init__(self):
            pass

    o = Dummy()
    o.parsed = [{"name": "foo"}, {"name": "bar"}]

    p = P()
    p.blocks = {"Products": o}
    p.parsed = {"metadata": {}}

    assert name_for_process(p, "no") == "MFP: foo⧺bar"


def test_name_for_waste_treatment_products_clean_name():
    class Dummy:
        pass

    class P(Process):
        def __init__(self):
            pass

    o = Dummy()
    o.parsed = [
        {"name": r"Albacore, fillet, raw, at processing {FR} U"},
        {"name": r"Albacore, residues, raw, at processing {FR} U"},
    ]

    p = P()
    p.blocks = {"Waste treatment": o}
    p.parsed = {"metadata": {}}

    assert name_for_process(p, "no") == "MFP: Albacore, fillet, raw, at⧺Albacore, residues, raw"
