from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.blocks import ImpactCategory


def test_impact_category(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "damagecategory.txt")
    pip = [elem.parsed for elem in obj.blocks if isinstance(elem, ImpactCategory)]
    assert len(pip) == 4
    assert pip[0] == {
        "name": "NORM - HH - Releases",
        "unit": "man.SV",
        "cfs": [
            {
                "context": ("Air", "(unspecified)"),
                "name": "Lead-210",
                "cas_number": "14255-04-0",
                "factor": 1.28e-6,
                "unit": "kBq",
                "line_no": 45,
            },
            {
                "context": ("Water", "(unspecified)"),
                "name": "Lead-210",
                "cas_number": None,
                "factor": 4.03e-9,
                "unit": "kBq",
                "line_no": 46,
            },
        ],
    }
