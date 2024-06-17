from .blocks import (
    GenericUncertainBiosphere,
    Process,
    Products,
    SimaProCSVBlock,
    TechnosphereEdges,
    Units,
    WasteTreatment,
)

HAS_UNITS = (
    GenericUncertainBiosphere,
    Products,
    TechnosphereEdges,
    WasteTreatment,
)

from loguru import logger

from .uncertainty import recalculate_uncertainty_distribution

missing_units = set()


def normalize_units(blocks: list[SimaProCSVBlock]) -> list[SimaProCSVBlock]:
    """Convert all values to the base unit.

    Need to change:
    * amount
    * formula
    * uncertainty distribution

    """
    unit_mapping = {
        o["name"]: o
        for block in filter(lambda x: isinstance(x, Units), blocks)
        for o in block.parsed
    }

    for process_block in filter(lambda x: isinstance(x, Process), blocks):
        for block in filter(lambda x: isinstance(x, HAS_UNITS), process_block.blocks.values()):
            for obj in block.parsed:
                try:
                    mapping = unit_mapping[obj["unit"]]
                    if mapping["reference unit name"] != obj["unit"]:
                        logger.debug(
                            "Changing units from {a} to {b} with conversion factor {c} on line {d}",
                            a=obj["unit"],
                            b=mapping["reference unit name"],
                            c=mapping["conversion"],
                            d=obj["line_no"],
                        )
                        obj["unit"] = mapping["reference unit name"]
                        if "formula" in obj:
                            obj["formula"] = f"({obj['formula']}) * {mapping['conversion']}"
                        if "uncertainty type" in obj:
                            recalculate_uncertainty_distribution(obj, mapping["conversion"])
                        else:
                            obj["amount"] *= mapping["conversion"]
                except KeyError:
                    if obj["unit"] not in missing_units:
                        missing_units.add(obj["unit"])
                        logger.warning("Unknown unit {unit} used on line {line_no}", **obj)
