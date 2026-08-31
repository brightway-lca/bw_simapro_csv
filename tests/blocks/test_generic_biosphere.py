import pytest

from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.blocks import Process
from bw_simapro_csv.blocks.generic_biosphere import GenericUncertainBiosphere
from bw_simapro_csv.errors import UnparsableLine


def test_non_material_emission_singular(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "non_material_emission_singular.csv", database_name="test")
    process = next(block for block in obj.blocks if isinstance(block, Process))

    assert "Non material emission" in process.blocks
    block = process.blocks["Non material emission"]
    assert isinstance(block, GenericUncertainBiosphere)
    assert [line["name"] for line in block.parsed] == ["Noise"]

    # The singular heading is a heading, not a data row of the preceding block
    assert [line["name"] for line in process.blocks["Emissions to air"].parsed] == ["Ammonia"]


def test_short_line_names_offending_row():
    with pytest.raises(UnparsableLine) as excinfo:
        GenericUncertainBiosphere(
            block=[(12, ["Unknown heading"])],
            header={"decimal_separator": "."},
            category="Emissions to air",
        )

    message = str(excinfo.value)
    assert "Unknown heading" in message
    assert "Emissions to air" in message
    assert "12" in message


def test_unknown_heading_raises_unparsable_line(fixtures_dir):
    """An unrecognized heading is given to the previous block as a data row"""
    with pytest.raises(UnparsableLine) as excinfo:
        SimaProCSV(fixtures_dir / "unknown_block_heading.csv", database_name="test")

    message = str(excinfo.value)
    assert "Bogus emissions" in message
    assert "Final waste flows" in message
