from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.blocks import NormalizationWeightingSet


def test_impact_category_complete():
    data = [
        ("IMPACT World+ (Stepwise 2006 values)",),
        ("",),
        ("Normalization",),
        ("Human health", "1.37E+01"),
        ("Ecosystem quality", "1.01E-04"),
        ("",),
        ("Weighting",),
        ("Human health", "5401.459854"),
        ("Ecosystem quality", "1386.138614"),
    ]
    parsed = NormalizationWeightingSet(data, None).parsed
    assert parsed == {
        "name": "IMPACT World+ (Stepwise 2006 values)",
        "normalization": [
            {
                "category": ("Human health"),
                "factor": 13.7,
            },
            {
                "category": "Ecosystem quality",
                "factor": 1.01e-4,
            },
        ],
        "weighting": [
            {
                "category": ("Human health"),
                "factor": 5401.459854,
            },
            {
                "category": "Ecosystem quality",
                "factor": 1386.138614,
            },
        ],
    }


def test_impact_category_partial():
    data = [
        ("IMPACT World+ (Stepwise 2006 values)",),
        ("",),
        ("Weighting",),
        ("Human health", "5401.459854"),
        ("Ecosystem quality", "1386.138614"),
    ]
    parsed = NormalizationWeightingSet(data, None).parsed
    assert parsed == {
        "name": "IMPACT World+ (Stepwise 2006 values)",
        "normalization": [],
        "weighting": [
            {
                "category": ("Human health"),
                "factor": 5401.459854,
            },
            {
                "category": "Ecosystem quality",
                "factor": 1386.138614,
            },
        ],
    }

    data = [
        ("IMPACT World+ (Stepwise 2006 values)",),
        ("",),
        ("Normalization",),
        ("Human health", "1.37E+01"),
        ("Ecosystem quality", "1.01E-04"),
    ]
    parsed = NormalizationWeightingSet(data, None).parsed
    assert parsed == {
        "name": "IMPACT World+ (Stepwise 2006 values)",
        "normalization": [
            {
                "category": ("Human health"),
                "factor": 13.7,
            },
            {
                "category": "Ecosystem quality",
                "factor": 1.01e-4,
            },
        ],
        "weighting": [],
    }
