from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.blocks import Process
from bw_simapro_csv.blocks.generic_biosphere import GenericUncertainBiosphere


def test_non_material_emission_singular(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "non_material_emission_singular.csv", database_name="test")
    process = next(block for block in obj.blocks if isinstance(block, Process))

    assert "Non material emission" in process.blocks
    block = process.blocks["Non material emission"]
    assert isinstance(block, GenericUncertainBiosphere)
    assert [line["name"] for line in block.parsed] == ["Noise"]

    # The singular heading is a heading, not a data row of the preceding block
    assert [line["name"] for line in process.blocks["Emissions to air"].parsed] == ["Ammonia"]
