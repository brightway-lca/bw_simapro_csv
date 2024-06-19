from collections import defaultdict

from loguru import logger

from .blocks import (
    GenericUncertainBiosphere,
    Process,
    Products,
    SimaProCSVBlock,
    TechnosphereEdges,
    Units,
    WasteTreatment,
)
from .uncertainty import recalculate_uncertainty_distribution

HAS_UNITS = (
    GenericUncertainBiosphere,
    Products,
    TechnosphereEdges,
    WasteTreatment,
)

missing_units = set()
unit_conversions = set()


def normalize_units(blocks: list[SimaProCSVBlock]) -> None:
    """Convert all values to the base unit.

    Need to change:
    * amount
    * formula
    * uncertainty distribution

    """
    unit_conversion_check = defaultdict(list)
    for block in filter(lambda x: isinstance(x, Units), blocks):
        for o in block.parsed:
            unit_conversion_check[o["name"]].append(o)

    for key, values in unit_conversion_check.items():
        if len(values) > 1 and len({v["conversion"] for v in values}) > 1:
            logger.critical(
                """
    Multiple different unit conversions given for input unit "{a}".
    After removing illegal characters and fixing potential encoding issues,
    unit "{a}" has multiple possible conversion factors. This will lead to
    incorrect results and undefined behaviour. To fix this, please remove
    all unwanted unit conversions lines. We found the follow possible conversions:
    Source unit; target unit; conversion; line number:{b}""",
                a=key,
                b="\n\t"
                + "\n\t".join(
                    [
                        str((v["name"], v["reference unit name"], v["conversion"], v["line_no"]))
                        for v in values
                    ]
                ),
            )

    unit_mapping = {
        o["name"]: o
        for block in filter(lambda x: isinstance(x, Units), blocks)
        for o in block.parsed
    }

    for mapping in unit_mapping.values():
        if mapping["name"] == mapping["reference unit name"] and mapping["conversion"] != 1:
            logger.critical(
                """
    Possible unit error which requires a manual check.
    After removing illegal characters and fixing potential encoding issues,
    unit "{a}" is identical to reference unit "{b}",
    but the conversion factor is given as {c}.
    Please look at line {d} to see the original label of this unit.
    It would be best to rename or delete this unit if possible.""",
                a=mapping["name"],
                b=mapping["reference unit name"],
                c=mapping["conversion"],
                d=mapping["line_no"],
            )

    for process_block in filter(lambda x: isinstance(x, Process), blocks):
        for block in filter(lambda x: isinstance(x, HAS_UNITS), process_block.blocks.values()):
            for obj in block.parsed:
                try:
                    mapping = unit_mapping[obj["unit"]]
                    if mapping["reference unit name"] != obj["unit"]:
                        if (
                            key := (obj["unit"], mapping["reference unit name"])
                        ) not in unit_conversions:
                            unit_conversions.add(key)
                            logger.debug(
                                "Changing units from {a} to {b} with conversion factor {c} on line {d}",
                                a=obj["unit"],
                                b=mapping["reference unit name"],
                                c=mapping["conversion"],
                                d=obj["line_no"],
                            )
                        obj["original unit before conversion"] = obj["unit"]
                        obj["unit conversion factor"] = mapping["conversion"]
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
