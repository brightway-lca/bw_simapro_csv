from numbers import Number

from bw_simapro_csv import SimaProCSV


def test_issue_18(fixtures_dir):
    given = SimaProCSV(fixtures_dir / "project_params.csv")

    assert len(given.blocks) == 5

    mat_fuel = given.blocks[1].blocks["Materials/fuels"].parsed
    assert mat_fuel[0]["formula"] == "((4.8 * SP_VARIABLE_NAME) / ((7 * 0.9) - 3))"
    assert mat_fuel[0]["original_formula"] == "4.8*variable_name/((7*0.9)-3)"
    assert isinstance(mat_fuel[0]["amount"], Number)

    assert given.blocks[-1].parsed == [
        {
            "uncertainty type": 0,
            "loc": 1.0,
            "amount": 1.0,
            "name": "SP_VARIABLE_NAME",
            "hidden": False,
            "comment": "Used for sensitivity",
            "line_no": 222,
            "original_name": "variable_name",
        }
    ]
