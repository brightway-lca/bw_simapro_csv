from ..constants import MAGIC
from ..utils import add_amount_or_formula, get_key_multiline_values, jump_to_nonempty, skip_empty
from .base import SimaProCSVBlock
from .calculated_parameters import DatasetCalculatedParameters
from .parameters import DatasetInputParameters
from .technosphere_edges import TechnosphereEdges


class ProductStageReference(SimaProCSVBlock):
    """The reference output of a product stage - its ``Products`` line.

    A product-stage reference row is laid out differently from a process
    ``Products`` row. A process row carries allocation and waste-type columns:

    ```
    name;unit;amount;allocation;waste type;category;comment
    ```

    A product stage (an assembly, life cycle, ...) is never allocated, so its
    reference row omits those columns:

    ```
    name;unit;amount;category;comment
    ```

    Reusing the process ``Products`` parser here would read the wrong columns (and
    index past the end of the row), so the product stage gets its own reference
    parser. Indices past the row length degrade to empty strings rather than
    raising, since trailing columns are routinely dropped by SimaPro.
    """

    def __init__(self, block: list[tuple], header: dict, **kwargs):
        self.parsed = []
        self.has_formula = True

        for line_no, line in skip_empty(block):
            self.parsed.append(
                add_amount_or_formula(
                    {
                        "name": line[0],
                        "unit": line[1] if len(line) > 1 else "",
                        "category": line[3] if len(line) > 3 else "",
                        "comment": line[4] if len(line) > 4 else "",
                        "line_no": line_no,
                    },
                    line[2] if len(line) > 2 else "",
                    header["decimal_separator"],
                )
            )


class RawProductStageSection(SimaProCSVBlock):
    """Fallback for a product-stage sub-section without a dedicated parser.

    SimaPro product stages can carry scenario sections (disposal, reuse, ...)
    whose exact column layout we do not model. Rather than dropping them - the
    behaviour this class replaces routed the whole product stage to a no-op that
    discarded all of its content - we keep their rows verbatim so the block still
    carries everything the file held.
    """

    def __init__(self, block: list[tuple], header: dict, category: str, **kwargs):
        self.category = category
        self.parsed = [
            {"line_no": line_no, "fields": list(line)} for line_no, line in skip_empty(block)
        ]


# SimaPro product-stage sub-sections. The reference output is the stage's own
# ``Products`` row; every component section (sub-assemblies, processes, scenarios)
# shares the technosphere-edge row layout ``name;unit;amount;uncertainty...;comment``.
# Sections we have not seen a sample of fall back to ``RawProductStageSection`` so
# nothing is silently dropped.
PRODUCT_STAGE_BLOCK_MAPPING = {
    "Products": ProductStageReference,
    "Materials/assemblies": TechnosphereEdges,
    "Processes": TechnosphereEdges,
    "Assembly": TechnosphereEdges,
    "Subassemblies": TechnosphereEdges,
    "Additional life cycles": TechnosphereEdges,
    "Disassembly": TechnosphereEdges,
    "Reuse": TechnosphereEdges,
    "Disposal scenario": TechnosphereEdges,
    "Waste/Disposal scenario": TechnosphereEdges,
    "Waste scenario": TechnosphereEdges,
    "Input parameters": DatasetInputParameters,
    "Calculated parameters": DatasetCalculatedParameters,
}


class ProductStage(SimaProCSVBlock):
    """A SimaPro product stage: an assembly, life cycle, or scenario.

    ``{product stages}`` exports interleave these blocks with ordinary
    ``Process`` blocks. SimaPro builds the modelled product by composing *named*
    references: an assembly's ``Materials/assemblies`` and ``Processes`` sections
    point at other product stages and at processes by name (a product stage has
    no ``Process identifier``), and its ``Products`` section is the stage's
    reference output. Before this class, ``Product stage`` blocks were routed to a
    no-op and their entire content was discarded; we now parse them the same way
    ``Process`` does - metadata pairs, then typed sub-blocks - so downstream code
    can read ``.parsed["metadata"]`` and ``.blocks[...]`` symmetrically with a
    process. A product stage is identified by its reference-product name.
    """

    def __init__(self, block: list[list], header: dict):
        self.parsed = {"metadata": {}}
        self.blocks = {}
        self.header = header

        block = jump_to_nonempty(block)

        # Metadata is stored as alternating key / value lines (the value may be
        # blank), up to the first sub-block header. Unlike a process, a product
        # stage carries no Date/Infrastructure/Literature-reference metadata, so a
        # plain key/value pull is enough.
        self.index = 0
        while (
            self.index < len(block)
            and block[self.index][1]
            and block[self.index][1][0] not in PRODUCT_STAGE_BLOCK_MAPPING
        ):
            key, value = self.pull_metadata_pair(block)
            if value:
                self.parsed["metadata"][key] = value

        for block_type, block_data in get_key_multiline_values(
            block[self.index :], stop_terms=PRODUCT_STAGE_BLOCK_MAPPING
        ):
            if not block_data:
                continue
            block_class = PRODUCT_STAGE_BLOCK_MAPPING.get(block_type, RawProductStageSection)
            self.blocks[block_type] = block_class(
                header=header, block=block_data, category=block_type
            )

    def pull_metadata_pair(self, block: list[list]) -> tuple[str, str]:
        """Read a ``key`` / ``value`` metadata pair, then skip to the next
        non-empty line. The value may be blank or span multiple cells on its line."""
        key = block[self.index][1][0]
        value_line = block[self.index + 1][1] if self.index + 1 < len(block) else []
        value = MAGIC.join([elem for elem in value_line if elem]) if value_line else ""
        self.index += 2
        while self.index < len(block) and not any(block[self.index][1]):
            self.index += 1
        return key, value
