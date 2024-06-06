from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.blocks import Method


def test_method_block_missing(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "header.csv")
    pip = [elem.parsed for elem in obj.blocks if isinstance(elem, Method)]
    assert pip == []


def test_method_block(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "damagecategory.txt")
    pip = [elem.parsed for elem in obj.blocks if isinstance(elem, Method)]
    assert pip == [{
        'Name': 'DC Test',
        'Version': ("1", "8"),
        'Comment': "Damage category import testing",
        "Category": "Others\\NORM",
        "Use Damage Assessment": True,
        "Use Normalization": False,
        "Use Weighting": False,
        "Use Addition": False,
    }]
