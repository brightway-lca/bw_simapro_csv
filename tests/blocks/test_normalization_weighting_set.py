from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.blocks import NormalizationWeightingSet


def test_impact_category_complete():
    data = [
        (0, ("IMPACT World+ (Stepwise 2006 values)",)),
        (1, ("",)),
        (2, ("Normalization",)),
        (3, ("Human health", "1.37E+01")),
        (4, ("Ecosystem quality", "1.01E-04")),
        (5, ("",)),
        (6, ("Weighting",)),
        (7, ("Human health", "5401.459854")),
        (8, ("Ecosystem quality", "1386.138614")),
    ]
    parsed = NormalizationWeightingSet(data, None).parsed
    assert parsed == {
        "name": "IMPACT World+ (Stepwise 2006 values)",
        "normalization": [
            {
                "category": ("Human health"),
                "factor": 13.7,
                "line_no": 3,
            },
            {
                "category": "Ecosystem quality",
                "factor": 1.01e-4,
                "line_no": 4,
            },
        ],
        "weighting": [
            {
                "category": ("Human health"),
                "factor": 5401.459854,
                "line_no": 7,
            },
            {
                "category": "Ecosystem quality",
                "factor": 1386.138614,
                "line_no": 8,
            },
        ],
    }


def test_impact_category_partial():
    data = [
        (0, ("IMPACT World+ (Stepwise 2006 values)",)),
        (1, ("",)),
        (2, ("Weighting",)),
        (3, ("Human health", "5401.459854")),
        (4, ("Ecosystem quality", "1386.138614")),
    ]
    parsed = NormalizationWeightingSet(data, None).parsed
    assert parsed == {
        "name": "IMPACT World+ (Stepwise 2006 values)",
        "normalization": [],
        "weighting": [
            {
                "category": ("Human health"),
                "factor": 5401.459854,
                "line_no": 3,
            },
            {
                "category": "Ecosystem quality",
                "factor": 1386.138614,
                "line_no": 4,
            },
        ],
    }

    data = [
        (0, ("IMPACT World+ (Stepwise 2006 values)",)),
        (1, ("",)),
        (2, ("Normalization",)),
        (3, ("Human health", "1.37E+01")),
        (4, ("Ecosystem quality", "1.01E-04")),
    ]
    parsed = NormalizationWeightingSet(data, None).parsed
    assert parsed == {
        "name": "IMPACT World+ (Stepwise 2006 values)",
        "normalization": [
            {
                "category": ("Human health"),
                "factor": 13.7,
                "line_no": 3,
            },
            {
                "category": "Ecosystem quality",
                "factor": 1.01e-4,
                "line_no": 4,
            },
        ],
        "weighting": [],
    }
