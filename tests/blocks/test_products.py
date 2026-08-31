from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.blocks import Process
from bw_simapro_csv.utils import remove_trailing_percentage


def test_allocation_with_percentage_sign(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "allocation_percentage.csv", database_name="test")
    process = next(block for block in obj.blocks if isinstance(block, Process))

    product = process.blocks["Products"].parsed[0]
    assert product["name"] == "Test product"
    assert product["allocation"] == 100
    assert "allocation_formula" not in product


def test_remove_trailing_percentage():
    assert remove_trailing_percentage("100%") == "100"
    assert remove_trailing_percentage(" 100 % ") == "100"
    assert remove_trailing_percentage("100") == "100"
    assert remove_trailing_percentage("") == ""
    assert remove_trailing_percentage("x * 2") == "x * 2"
