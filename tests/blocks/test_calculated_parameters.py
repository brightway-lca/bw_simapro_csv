from bw_simapro_csv.blocks import DatabaseCalculatedParameters, ProjectCalculatedParameters


def test_database_calculated_parameters():
    given = DatabaseCalculatedParameters(
        [
            (0, ("empty", "1/load", "")),
            (1, ("m1", "Iff(m=1; 1; 0)", "")),
            (
                2,
                (
                    "Conv_STon_MTon",
                    "2/2,20462",
                    "Convert short ton  (U.S. ton) to metric ton (tonne)",
                ),
            ),
        ],
        {"decimal_separator": ","},
    )
    expected = [
        {
            "name": "empty",
            "formula": "1/load",
            "line_no": 0,
            "comment": "",
        },
        {
            "name": "m1",
            "formula": "Iff(m=1; 1; 0)",
            "line_no": 1,
            "comment": "",
        },
        {
            "name": "Conv_STon_MTon",
            "formula": "2/2.20462",
            "line_no": 2,
            "comment": "Convert short ton  (U.S. ton) to metric ton (tonne)",
        },
    ]
    assert given.parsed == expected


def test_project_calculated_parameters():
    given = ProjectCalculatedParameters(
        [
            (0, ("empty", "1/load", "")),
            (1, ("m1", "Iff(m=1; 1; 0)", "")),
            (
                2,
                (
                    "Conv_STon_MTon",
                    "2/2,20462",
                    "Convert short ton  (U.S. ton) to metric ton (tonne)",
                ),
            ),
        ],
        {"decimal_separator": ","},
    )
    expected = [
        {
            "name": "empty",
            "formula": "1/load",
            "line_no": 0,
            "comment": "",
        },
        {
            "name": "m1",
            "formula": "Iff(m=1; 1; 0)",
            "line_no": 1,
            "comment": "",
        },
        {
            "name": "Conv_STon_MTon",
            "formula": "2/2.20462",
            "line_no": 2,
            "comment": "Convert short ton  (U.S. ton) to metric ton (tonne)",
        },
    ]
    assert given.parsed == expected
