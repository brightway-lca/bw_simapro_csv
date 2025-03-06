import math

from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.blocks import Process


def test_waste_block(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "waste.csv")
    waste = [
        process.blocks["Waste treatment"]
        for process in filter(lambda x: isinstance(x, Process), obj.blocks)
    ][0]

    assert len(waste.parsed) == 1
    w = waste.parsed[0]

    assert (
        w["name"]
        == "Treatment of green waste, co-composting greenwaste-solid fraction of slurry 3-97, allocation cut-off on process {RER} U"
    )
    assert w["unit"] == "kg"
    assert w["waste_type"] == "All waste types"
    assert w["category"] == "Biowaste\\Transformation"
    assert (
        w["comment"]
        == "Composting of dehydrated manure (30-50% DM). Manure includes the impacts of dehydration."
    )
    assert w["formula"] == "(((1034 * 0.6684) * 0.59) * 0.03)"
    assert math.isclose(w["amount"], 1034 * 0.6684 * 0.59 * 0.03)
