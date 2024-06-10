from bw_simapro_csv.blocks import DatabaseCalculatedParameters, ProjectCalculatedParameters


def test_database_calculated_parameters():
    given = DatabaseCalculatedParameters(
        [
            ("empty", "1/load", ""),
            ("m1", "Iff(m=1; 1; 0)", ""),
            ("Conv_STon_MTon", "2/2,20462", "Convert short ton  (U.S. ton) to metric ton (tonne)"),
        ],
        None,
    )
    expected = [
        {
            "label": "empty",
            "formula": "1/load",
            "comment": "",
        },
        {
            "label": "m1",
            "formula": "Iff(m=1; 1; 0)",
            "comment": "",
        },
        {
            "label": "Conv_STon_MTon",
            "formula": "2/2,20462",
            "comment": "Convert short ton  (U.S. ton) to metric ton (tonne)",
        },
    ]
    assert given.parsed == expected


def test_project_calculated_parameters():
    given = ProjectCalculatedParameters(
        [
            ("empty", "1/load", ""),
            ("m1", "Iff(m=1; 1; 0)", ""),
            ("Conv_STon_MTon", "2/2,20462", "Convert short ton  (U.S. ton) to metric ton (tonne)"),
        ],
        None,
    )
    expected = [
        {
            "label": "empty",
            "formula": "1/load",
            "comment": "",
        },
        {
            "label": "m1",
            "formula": "Iff(m=1; 1; 0)",
            "comment": "",
        },
        {
            "label": "Conv_STon_MTon",
            "formula": "2/2,20462",
            "comment": "Convert short ton  (U.S. ton) to metric ton (tonne)",
        },
    ]
    assert given.parsed == expected
