from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.blocks import Quantities


def test_process_metadata(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "process.csv")
    quans = [elem.parsed for elem in obj.blocks if isinstance(elem, Quantities)]
    assert len(quans) == 1
    expected = {
        "Mass": True,
        "Energy": True,
        "Length": True,
    }
    assert quans[0] == expected
