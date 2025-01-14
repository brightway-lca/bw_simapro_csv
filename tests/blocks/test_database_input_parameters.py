import math
from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.blocks import DatabaseInputParameters


def test_db_input_params_empty(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "process_with_invalid_lognormal_scale.csv")
    dip = [elem.parsed for elem in obj.blocks if isinstance(elem, DatabaseInputParameters)]
    assert dip == []


def test_db_input_params(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "process.csv")
    dip = [elem.parsed for elem in obj.blocks if isinstance(elem, DatabaseInputParameters)][0]
    assert dip == [
        {
            "uncertainty type": 2,
            "amount": 1.0,
            "loc": 0.0,
            "scale": math.log(2),
            "line_no": 274,
            "negative": False,
            "hidden": False,
            "original_name": "db_input_param",
            "name": "SP_DB_INPUT_PARAM",
            "comment": "database parameter",
        }
    ]
