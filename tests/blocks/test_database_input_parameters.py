from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.blocks import DatabaseInputParameters


def test_db_input_params_empty(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "stages.csv")
    dip = [elem.parsed for elem in obj.blocks if isinstance(elem, DatabaseInputParameters)][0]
    assert dip == []


def test_db_input_params(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "process.csv")
    dip = [elem.parsed for elem in obj.blocks if isinstance(elem, DatabaseInputParameters)][0]
    assert dip == [
        {
            "uncertainty type": 2,
            "amount": 1.0,
            "loc": 0.0,
            "scale": 0.0,
            "line_no": 271,
            "negative": False,
            "hidden": False,
            "name": "db_input_param",
            "comment": "database parameter",
        }
    ]
