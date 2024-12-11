from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.blocks import GenericBiosphere
from bw_simapro_csv.cas import calculate_check_digit, validate_cas_string


def test_calculate_check_digit():
    assert calculate_check_digit("773218") == 5
    assert calculate_check_digit("778240") == 3


def test_validate_cas_string():
    assert validate_cas_string("7782425") == "7782-42-5"
    assert validate_cas_string("007782425") == "7782-42-5"
    assert validate_cas_string("  7782-42-5\n") == "7782-42-5"
    assert validate_cas_string("007782-42-5") == "7782-42-5"
    assert validate_cas_string("1228284-64-") == "1228284-64-7"
    assert validate_cas_string("") is None
    assert validate_cas_string(None) is None
    assert validate_cas_string(float("NaN")) is None
    assert validate_cas_string("7782-425") is None
    assert validate_cas_string("7782424") is None


def test_cas_in_file(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "cas_missing_check_number.csv")
    blocks = [
        elem
        for elem in obj.blocks
        if isinstance(elem, GenericBiosphere) and elem.category == "Emissions to soil"
    ]
    expected = [None, "1228284-64-7"]
    assert [obj["cas_number"] for obj in blocks[0].parsed] == expected
