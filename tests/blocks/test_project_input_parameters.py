from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.blocks import ProjectInputParameters


def test_db_input_params_empty(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "process_with_invalid_lognormal_scale.csv")
    pip = [elem.parsed for elem in obj.blocks if isinstance(elem, ProjectInputParameters)]
    assert pip == []


def test_db_input_params(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "process.csv")
    pip = [elem.parsed for elem in obj.blocks if isinstance(elem, ProjectInputParameters)][0]
    assert pip == [
        {
            "uncertainty type": 4,
            "amount": 32.0,
            "loc": 32.0,
            "minimum": 10.0,
            "maximum": 35.0,
            "line_no": 284,
            "negative": False,
            "hidden": False,
            "original_name": "proj_input_param",
            "name": "SP_PROJ_INPUT_PARAM",
            "comment": "project input parameter",
        }
    ]
