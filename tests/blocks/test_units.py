from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.blocks import Units


def test_units_block_missing(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "header.csv")
    pip = [elem.parsed for elem in obj.blocks if isinstance(elem, Units)]
    assert pip == []


def test_units_blocks_tab_delimiter(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "damagecategory.txt")
    pip = [elem.parsed for elem in obj.blocks if isinstance(elem, Units)][0]
    assert pip == [
        {
            "name": "Pt",
            "dimension": "Indicator",
            "conversion": 1.0,
            "reference unit name": "Pt",
            "line_no": 95,
        },
        {
            "name": "Bq",
            "dimension": "Radioactivity",
            "conversion": 1.0,
            "line_no": 96,
            "reference unit name": "Bq",
        },
        {
            "name": "kBq",
            "dimension": "Radioactivity",
            "conversion": 1000.0,
            "line_no": 97,
            "reference unit name": "Bq",
        },
        {
            "name": "mBq",
            "dimension": "Radioactivity",
            "conversion": 0.001,
            "line_no": 98,
            "reference unit name": "Bq",
        },
        {
            "name": "µPt",
            "dimension": "Indicator",
            "conversion": 1e-06,
            "reference unit name": "Pt",
            "line_no": 99,
        },
        {
            "name": "nPt",
            "dimension": "Indicator",
            "conversion": 1e-09,
            "reference unit name": "Pt",
            "line_no": 100,
        },
        {
            "name": "kPt",
            "dimension": "Indicator",
            "conversion": 1000.0,
            "line_no": 101,
            "reference unit name": "Pt",
        },
        {
            "name": "MPt",
            "dimension": "Indicator",
            "conversion": 1000000.0,
            "line_no": 102,
            "reference unit name": "Pt",
        },
        {
            "name": "GPt",
            "dimension": "Indicator",
            "conversion": 1000000000.0,
            "line_no": 103,
            "reference unit name": "Pt",
        },
        {
            "name": "mPt",
            "dimension": "Indicator",
            "conversion": 0.001,
            "reference unit name": "Pt",
            "line_no": 104,
        },
        {
            "name": "µBq",
            "dimension": "Radioactivity",
            "conversion": 1e-06,
            "line_no": 105,
            "reference unit name": "Bq",
        },
        {
            "name": "nBq",
            "dimension": "Radioactivity",
            "conversion": 1e-09,
            "line_no": 106,
            "reference unit name": "Bq",
        },
    ]


def test_units_block_encoding(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "weird_units.csv")
    pip = [elem.parsed for elem in obj.blocks if isinstance(elem, Units)][0]
    expected = [
        {
            "conversion": 1e-09,
            "dimension": "Mass",
            "name": "¾g",
            "reference unit name": "kg",
        },
        {
            "conversion": 833.0,
            "dimension": "Mass",
            "name": "BCAPU",
            "reference unit name": "kg",
        },
        {
            "conversion": 1.0,
            "dimension": "Mass",
            "name": "MEU",
            "reference unit name": "kg",
        },
        {
            "conversion": 1.0,
            "dimension": "Energy",
            "name": "T.R.",
            "reference unit name": "MJ",
        },
        {
            "conversion": 1000000000.0,
            "dimension": "Volume",
            "name": "TL",
            "reference unit name": "m3",
        },
        {
            "conversion": 1000000.0,
            "dimension": "Volume",
            "name": "GL",
            "reference unit name": "m3",
        },
        {
            "conversion": 1e-09,
            "dimension": "Mass",
            "name": "Ãg",
            "reference unit name": "kg",
        },
        {
            "conversion": 1.0,
            "dimension": "Mass",
            "name": "kgCOD",
            "reference unit name": "kg",
        },
        {
            "conversion": 1000.0,
            "dimension": "Volume",
            "name": "Ml",
            "reference unit name": "m3",
        },
        {
            "conversion": 1.0,
            "dimension": "Mass",
            "name": "aaa",
            "reference unit name": "kg",
        },
        {
            "conversion": 56.6,
            "dimension": "Energy",
            "name": "kg-NO",
            "reference unit name": "MJ",
        },
        {
            "conversion": 49.3,
            "dimension": "Energy",
            "name": "kg-RU",
            "reference unit name": "MJ",
        },
        {
            "conversion": 47.0,
            "dimension": "Energy",
            "name": "kg-GB",
            "reference unit name": "MJ",
        },
        {
            "conversion": 49.7,
            "dimension": "Energy",
            "name": "kg-DZ",
            "reference unit name": "MJ",
        },
        {
            "conversion": 45.9,
            "dimension": "Energy",
            "name": "kg-DE",
            "reference unit name": "MJ",
        },
        {
            "conversion": 1000.0,
            "dimension": "Mass",
            "name": "T",
            "reference unit name": "kg",
        },
        {
            "conversion": 1e-09,
            "dimension": "Mass",
            "name": "'g",
            "reference unit name": "kg",
        },
        {
            "conversion": 1e-09,
            "dimension": "Mass",
            "name": "_g",
            "reference unit name": "kg",
        },
        {
            "conversion": 1e-09,
            "dimension": "Mass",
            "name": "Âg",
            "reference unit name": "kg",
        },
        {
            "conversion": 1e-09,
            "dimension": "Mass",
            "name": "•g",
            "reference unit name": "kg",
        },
        {
            "conversion": 1.64e-05,
            "dimension": "Volume",
            "name": "cuin",
            "reference unit name": "m3",
        },
        {
            "conversion": 1e-09,
            "dimension": "Mass",
            "name": "ï¾µg",
            "reference unit name": "kg",
        },
        {
            "conversion": 1e-09,
            "dimension": "Mass",
            "name": "ムg",
            "reference unit name": "kg",
        },
        {
            "conversion": 1e-09,
            "dimension": "Mass",
            "name": "ug",
            "reference unit name": "kg",
        },
        {
            "conversion": 1.0,
            "dimension": "Mass",
            "name": "100%",
            "reference unit name": "kg",
        },
        {
            "conversion": 1000.0,
            "dimension": "Mass",
            "name": "metric to.",
            "reference unit name": "kg",
        },
        {
            "conversion": 28.31685,
            "dimension": "Volume",
            "name": "MCF",
            "reference unit name": "m3",
        },
        {
            "conversion": 907184700.0,
            "dimension": "Mass",
            "name": "MT*",
            "reference unit name": "kg",
        },
        {
            "conversion": 28316.85,
            "dimension": "Volume",
            "name": "MMCF",
            "reference unit name": "m3",
        },
        {
            "conversion": 1e-09,
            "dimension": "Mass",
            "name": "5g",
            "reference unit name": "kg",
        },
        {
            "conversion": 1e-09,
            "dimension": "Mass",
            "name": "fg",
            "reference unit name": "kg",
        },
        {
            "conversion": 0.45454545,
            "dimension": "Mass",
            "name": "EU",
            "reference unit name": "kg",
        },
        {
            "conversion": 1.0,
            "dimension": "Volume",
            "name": "m3sub",
            "reference unit name": "m3",
        },
        {
            "conversion": 1e-09,
            "dimension": "Mass",
            "name": "�g",
            "reference unit name": "kg",
        },
        {
            "conversion": 1e-09,
            "dimension": "Mass",
            "name": "Â!!!g",
            "reference unit name": "kg",
        },
        {
            "conversion": 1e-09,
            "dimension": "Mass",
            "name": "?g",
            "reference unit name": "kg",
        },
        {
            "conversion": 0.02835,
            "dimension": "Mass",
            "name": "Oz",
            "reference unit name": "kg",
        },
        {
            "conversion": 0.02835,
            "dimension": "Mass",
            "name": "OA33z",
            "reference unit name": "kg",
        },
        {
            "conversion": 1.0,
            "dimension": "Energy",
            "name": "MJe",
            "reference unit name": "MJ",
        },
        {
            "conversion": 0.02834952,
            "dimension": "Mass",
            "name": "z",
            "reference unit name": "kg",
        },
        {
            "conversion": 1.0,
            "dimension": "Mass",
            "name": "kg N1",
            "reference unit name": "kg",
        },
        {
            "conversion": 1.0,
            "dimension": "Mass",
            "name": "kg enlevé",
            "reference unit name": "kg",
        },
        {
            "conversion": 1.0,
            "dimension": "Mass",
            "name": "kg enlevÅ½",
            "reference unit name": "kg",
        },
        {
            "conversion": 2.96e-05,
            "dimension": "Volume",
            "name": "oz (fl)",
            "reference unit name": "m3",
        },
        {
            "conversion": 1.0,
            "dimension": "Volume",
            "name": "M3",
            "reference unit name": "m3",
        },
        {
            "conversion": 1.0,
            "dimension": "Volume",
            "name": "Kl",
            "reference unit name": "m3",
        },
        {
            "conversion": 1000.0,
            "dimension": "Volume",
            "name": "kM3",
            "reference unit name": "m3",
        },
        {
            "conversion": 0.15898729,
            "dimension": "Volume",
            "name": "bbl",
            "reference unit name": "m3",
        },
        {
            "conversion": 1055.87,
            "dimension": "Energy",
            "name": "MMBtu",
            "reference unit name": "MJ",
        },
        {
            "conversion": 28.1685,
            "dimension": "Volume",
            "name": "Mscf",
            "reference unit name": "m3",
        },
        {
            "conversion": 27.21,
            "dimension": "Mass",
            "name": "Bushel",
            "reference unit name": "kg",
        },
        {
            "conversion": 1000000000.0,
            "dimension": "Mass",
            "name": "Mton",
            "reference unit name": "kg",
        },
        {
            "conversion": 1000000000.0,
            "dimension": "Volume",
            "name": "km3",
            "reference unit name": "m3",
        },
        {
            "conversion": 1000000.0,
            "dimension": "Volume",
            "name": "m3M",
            "reference unit name": "m3",
        },
        {
            "conversion": 1000000.0,
            "dimension": "Volume",
            "name": "M m3",
            "reference unit name": "m3",
        },
        {
            "conversion": 1e-09,
            "dimension": "Mass",
            "name": "Ag",
            "reference unit name": "kg",
        },
        {
            "conversion": 2.957353e-05,
            "dimension": "Volume",
            "name": "fl. oz",
            "reference unit name": "m3",
        },
        {
            "conversion": 0.00235974,
            "dimension": "Volume",
            "name": "BoardFoot",
            "reference unit name": "m3",
        },
    ]
    for index, line in enumerate(expected, start=96):
        line["line_no"] = index
    assert pip == expected
