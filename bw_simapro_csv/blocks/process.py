from bw2parameters import Interpreter, ParameterSet

from ..parameters import (
    FormulaSubstitutor,
    add_prefix_to_uppercase_input_parameters,
    substitute_in_formulas,
    prepare_formulas,
)
from ..utils import asboolean, asdate, get_key_multiline_values, jump_to_nonempty
from .base import SimaProCSVUncertainBlock
from .calculated_parameters import DatasetCalculatedParameters
from .generic_biosphere import GenericUncertainBiosphere
from .parameters import DatasetInputParameters
from .products import Products
from .technosphere_edges import TechnosphereEdges
from .wastes import RemainingWaste, SeparatedWaste, WasteScenario, WasteTreatment

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
        self.header = header

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

    def resolve_local_parameters(self, global_params: dict, substitutes: dict) -> None:
        """Resolve any formulae in input or output amounts, and convert raw data to parsed.

        Takes in parameter renames and amounts from project and database input parameters."""
        if "Input parameters" in self.blocks:
            add_prefix_to_uppercase_input_parameters(self.blocks["Input parameters"].parsed)
            substitutes = substitutes | {
                o["original_name"].upper(): o["name"]
                for o in self.blocks["Input parameters"].parsed
            }
            global_params = global_params | {
                o["name"]: o["amount"] for o in self.blocks["Input parameters"].parsed
            }

        if "Calculated parameters" in self.blocks:
            add_prefix_to_uppercase_input_parameters(prepare_formulas(self.blocks["Calculated parameters"].parsed, self.header))
            substitutes = substitutes | {
                o["original_name"].upper(): o["name"]
                for o in self.blocks["Calculated parameters"].parsed
            }
            visitor = FormulaSubstitutor(substitutes)
            for obj in self.blocks["Calculated parameters"].parsed:
                substitute_in_formulas(obj, visitor)
            ParameterSet(
                {o["name"]: o for o in self.blocks["Calculated parameters"].parsed}, global_params
            ).evaluate_and_set_amount_field()
            global_params = global_params | {
                o["name"]: o["amount"] for o in self.blocks["Calculated parameters"].parsed
            }
        else:
            visitor = FormulaSubstitutor(substitutes)

        interpreter = Interpreter()
        interpreter.add_symbols(global_params)

        for label, block in self.blocks.items():
            if not getattr(block, "has_formula", None):
                continue
            prepare_formulas(block.parsed, self.header)
            for obj in block.parsed:
                if "formula" in obj:
                    substitute_in_formulas(obj, visitor)
                    obj["amount"] = interpreter(obj["formula"])
