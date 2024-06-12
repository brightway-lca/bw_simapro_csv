from loguru import logger

from ..utils import asboolean, asdate, get_key_multiline_values, jump_to_nonempty
from .base import SimaProCSVUncertainBlock
from .calculated_parameters import DatasetCalculatedParameters
from .generic_biosphere import GenericUncertainBiosphere
from .parameters import DatasetInputParameters
from .products import Products
from .technosphere_edges import TechnosphereEdges
from .wastes import WasteTreatment, WasteScenario, SeparatedWaste, RemainingWaste

BLOCK_MAPPING = {
    "Avoided products": TechnosphereEdges,
    "Calculated parameters": DatasetCalculatedParameters,
    "Economic issues": GenericUncertainBiosphere,
    "Electricity/heat": TechnosphereEdges,
    "Emissions to air": GenericUncertainBiosphere,
    "Emissions to soil": GenericUncertainBiosphere,
    "Emissions to water": GenericUncertainBiosphere,
    "Final waste flows": GenericUncertainBiosphere,
    "Input parameters": DatasetInputParameters,
    "Materials/fuels": TechnosphereEdges,
    "Non material emissions": GenericUncertainBiosphere,
    "Products": Products,
    "Remaining waste": RemainingWaste,
    "Resources": GenericUncertainBiosphere,
    "Separated waste": SeparatedWaste,
    "Social issues": GenericUncertainBiosphere,
    "Waste scenario": WasteScenario,
    "Waste to treatment": TechnosphereEdges,
    "Waste treatment": WasteTreatment,
}


class Process(SimaProCSVUncertainBlock):
    """A life cycle inventory process, with inputs, products, and elementary exchanges"""

    def __init__(self, block: list[list], header: dict):
        self.parsed = {"metadata": {}}
        self.blocks = {}

        block = jump_to_nonempty(block)

        # Start with metadata. This is stored as:
        # Key
        # Value
        # On separate lines (value can span more than one line).
        # Also, sometimes the value is missing (blank line), so we can't use
        # `get_key_multiline_value`.
        self.index = 0
        while block[self.index][1][0] not in BLOCK_MAPPING:
            k, v = self.pull_metadata_pair(block, header)
            if v:
                self.parsed["metadata"][k] = v

        for block_type, block_data in get_key_multiline_values(
            block[self.index :], stop_terms=BLOCK_MAPPING
        ):
            kwargs = {
                "header": header,
                "block": block_data,
                "category": block_type,
            }
            if not block_data:
                continue
            self.blocks[block_type] = BLOCK_MAPPING[block_type](**kwargs)

    def pull_metadata_pair(self, block: list[list], header: dict) -> (str, str):
        key = block[self.index][1][0]

        if key == "Literature references":
            self.index += 1
            value = []
            while any(block[self.index][1]):
                reference = {"reference": block[self.index][1][0]}
                if len(block[self.index][1]) > 1:
                    reference["comment"] = block[self.index][1][1]
                value.append(reference)
                self.index += 1
        elif key == "Date":
            value = asdate(block[self.index + 1][1][0], dayfirst=header["dayfirst"])
            self.index += 2
        elif key == "Infrastructure":
            value = asboolean(block[self.index + 1][1][0])
            self.index += 2
        else:
            value = (
                " ⧺ ".join([elem for elem in block[self.index + 1][1] if elem])
                if block[self.index + 1][1]
                else ""
            )
            self.index += 2

        # Skip empty lines until next pair. Should only be one line, but life can be surprising
        while not any(block[self.index][1]):
            self.index += 1

        return key, value
