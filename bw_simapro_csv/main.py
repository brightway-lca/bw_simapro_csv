import csv
import datetime
import itertools
import json
import os
import shutil
import sys
from functools import partial
from io import StringIO
from pathlib import Path
from typing import Optional, Union

from bw2parameters import ParameterSet
from loguru import logger
from platformdirs import user_log_dir

from .blocks import (
    DamageCategory,
    DatabaseCalculatedParameters,
    DatabaseInputParameters,
    EmptyBlock,
    GenericBiosphere,
    ImpactCategory,
    LiteratureReference,
    Method,
    NormalizationWeightingSet,
    Process,
    ProjectCalculatedParameters,
    ProjectInputParameters,
    Quantities,
    SimaProCSVBlock,
    SystemDescription,
    Units,
)
from .csv_reader import BeKindRewind
from .errors import IndeterminateBlockEnd
from .header import SimaProCSVType, parse_header
from .parameters import (
    FormulaSubstitutor,
    add_prefix_to_uppercase_input_parameters,
    build_substitutes,
    prepare_formulas,
    substitute_in_formulas,
)
from .units import normalize_units
from .utils import json_serializer, parameter_set_evaluate_each_formula


def dummy(data, *args):
    return data


CONTROL_BLOCK_MAPPING = {
    "Database Calculated parameters": DatabaseCalculatedParameters,
    "Database Input parameters": DatabaseInputParameters,
    "Literature reference": LiteratureReference,
    "Project Input parameters": ProjectInputParameters,
    "Project Calculated parameters": ProjectCalculatedParameters,
    "Quantities": Quantities,
    "Product stage": dummy,
    "Units": Units,
    "Process": Process,
    "Method": Method,
    "Impact category": ImpactCategory,
    "Normalization-Weighting set": NormalizationWeightingSet,
    "Damage category": DamageCategory,
}

# These are lists of flows at the end of the file
INDETERMINATE_SECTION_HEADERS = {
    "Non material emissions": partial(GenericBiosphere, category="Non material emissions"),
    "Airborne emissions": partial(GenericBiosphere, category="Airborne emissions"),
    "Waterborne emissions": partial(GenericBiosphere, category="Waterborne emissions"),
    "Raw materials": partial(GenericBiosphere, category="Raw materials"),
    "Final waste flows": partial(GenericBiosphere, category="Final waste flows"),
    "Emissions to soil": partial(GenericBiosphere, category="Emissions to soil"),
    "Social issues": partial(GenericBiosphere, category="Social issues"),
    "Economic issues": partial(GenericBiosphere, category="Economic issues"),
    "System description": SystemDescription,
}

INDETERMINATE_SECTION_ERROR = """
    Flow lists are given at the end of this file, but the section headings for
    flow lists are also used in inventory process descriptions. We can normally
    use the text 'End' to show when a process block stops, but this file doesn't
    seem to use 'End' sections. We therefore can't tell if '{}' is a new block
    or not, and can't parse this file.
"""


class SimaProCSV:
    def __init__(
        self,
        path_or_stream: Union[Path, StringIO],
        encoding: str = "sloppy-windows-1252",
        database_name: Optional[str] = None,
        stderr_logs: bool = True,
        write_logs: bool = True,
        copy_logs: bool = False,
    ):
        """Read a SimaPro CSV file object, and parse the contents.

        We start with the header, as this defines how the rest of the file is to be parsed.
        It gives the CSV delimiter and decimal separator.

        We then break the file into logical chunks, such as processes or LCIA impact categories."""
        # Control logging level
        now = datetime.datetime.now().isoformat()[:19].replace(":", "-")

        if isinstance(path_or_stream, Path):
            if not path_or_stream.is_file():
                raise ValueError(f"Given `Path` {path_or_stream} is not a file")
            if not os.access(path_or_stream, os.R_OK):
                raise ValueError(f"File {path_or_stream} exists but lacks read permission")
            data = open(path_or_stream, encoding=encoding)
            self.logs_dir = (
                Path(user_log_dir("bw_simapro_csv", "pylca")) / f"{path_or_stream.stem}-{now}"
            )
            logger.info("Writing logs to {d}", d=str(self.logs_dir))
        elif not isinstance(path_or_stream, StringIO):
            raise ValueError(
                f"`path_or_stream` must be `Path` or `StringIO` - got {type(path_or_stream)}"
            )
        else:
            # We have to assume that the StringIO object was created with
            # some reasonable newline definition.
            data = path_or_stream
            self.logs_dir = Path(user_log_dir("bw_simapro_csv", "pylca")) / f"StringIO-{now}"

        self.configure_logs(stderr_logs, write_logs)

        # Converting Pydantic back to dict to release memory
        header, header_lines = parse_header(data)
        self.header = header.model_dump()

        if header.kind in (SimaProCSVType.processes, SimaProCSVType.stages):
            self.database_name = database_name or self.header["project"]
            if not self.database_name:
                raise ValueError(
                    "Can't find database name in parameter `database_name` or SimaPro header"
                )
            logger.info("Using database name '{n}'", n=self.database_name)

        self.uses_end_text = False
        self.filepath = str(path_or_stream) if isinstance(path_or_stream, Path) else "<StringIO>"

        logger.info(
            "SimaPro CSV import started.\n\tFile: '{file}'\n\tDelimiter: '{delimiter}'\n\tName: '{name}'",
            file=path_or_stream if isinstance(path_or_stream, Path) else "<StringIO>",
            delimiter="<tab>" if self.header["delimiter"] == "\t" else self.header["delimiter"],
            name=self.header["project"] or "(Not given)",
        )
        logger.debug(
            "Header information:\n\theader lines: {header_lines}\n\t{header}",
            header_lines=header_lines,
            header="\n\t".join(["{}: {}".format(k, v) for k, v in self.header.items()]),
        )

        if self.header["delimiter"] not in {";", ".", "\t", "|", " "}:
            logger.warning(f"SimaPro CSV file uses unusual delimiter '{self.header['delimiter']}'")

        rewindable_csv_reader = BeKindRewind(
            csv.reader(data, delimiter=self.header["delimiter"], strict=True),
            clean_elements=True,
            offset=header_lines,
        )

        self.blocks = []

        while block := self.get_next_block(rewindable_csv_reader, self.header):
            if block is not EmptyBlock:
                self.blocks.append(block)

        if header.kind in (SimaProCSVType.processes, SimaProCSVType.stages):
            self.resolve_parameters()

        normalize_units(self.blocks)

        if copy_logs:
            self.copy_log_dir(Path.cwd())

    def __iter__(self):
        return iter(self.blocks)

    def to_brightway(self, filepath: Optional[Path] = None) -> Union[dict, Path]:
        if self.header["kind"] == SimaProCSVType.processes:
            from .brightway import lci_to_brightway

            data = lci_to_brightway(self)
            if filepath is not None:
                with open(filepath, "w") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=json_serializer)
                return filepath
            else:
                return data
        else:
            raise TypeError("Only process exports are currently supported")

    def configure_logs(self, stderr_logs: bool, write_logs: bool) -> None:
        logger.remove()
        if stderr_logs:
            logger.add(sys.stderr, level="INFO")
        if write_logs:
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            logger.add(self.logs_dir / "debug.log", level="DEBUG")
            logger.add(self.logs_dir / "warning.log", level="WARNING")

    def copy_log_dir(self, base_dir: Path) -> None:
        """Copy the logs directory and its files to `base_dir`"""
        if not isinstance(base_dir, Path):
            raise ValueError(f"`base_dir` must be a `pathlib.Path` instance; got {type(base_dir)}")
        if not base_dir.is_dir():
            raise ValueError(f"`base_dir` must be an existing directory; got {type(base_dir)}")
        return shutil.copytree(self.logs_dir, base_dir / self.logs_dir.stem)

    def get_next_block(
        self, rewindable_csv_reader: BeKindRewind, header: dict
    ) -> Optional[SimaProCSVBlock]:
        data = []

        for line in rewindable_csv_reader:
            if not any(line):
                # Skip empty lines at beginning of block
                continue
            if len(line) == 1 and line[0] == "End":
                # Empty block
                self.uses_end_text = True
                return EmptyBlock
            # File object exhausted
            break
        else:
            # Already at end of file; return false-y result to break `while`
            return None

        block_type = line[0]
        if block_type in CONTROL_BLOCK_MAPPING:
            block_class = CONTROL_BLOCK_MAPPING[block_type]
        elif block_type in INDETERMINATE_SECTION_HEADERS:
            if not self.uses_end_text:
                raise IndeterminateBlockEnd(INDETERMINATE_SECTION_ERROR.format(block_type))
            block_class = INDETERMINATE_SECTION_HEADERS[block_type]
        else:
            raise ValueError(f"Can't process unknown block type {block_type}")

        for line in rewindable_csv_reader:
            if line and line[0] == "End":
                self.uses_end_text = True
                return block_class(data, header) if data else None
            if line and line[0] in CONTROL_BLOCK_MAPPING:
                rewindable_csv_reader.rewind()
                return block_class(data, header) if data else None
            data.append((rewindable_csv_reader.line_no, line))

        # EOF
        return block_class(data, header) if data else None

    def resolve_parameters(self) -> None:
        """Read in input parameters, and resolve formulas."""
        dcp = [
            add_prefix_to_uppercase_input_parameters(prepare_formulas(b.parsed, self.header))
            for b in self.blocks
            if isinstance(b, DatabaseCalculatedParameters)
        ]
        dip = [
            add_prefix_to_uppercase_input_parameters(b.parsed)
            for b in self.blocks
            if isinstance(b, DatabaseInputParameters)
        ]
        pcp = [
            add_prefix_to_uppercase_input_parameters(prepare_formulas(b.parsed, self.header))
            for b in self.blocks
            if isinstance(b, ProjectCalculatedParameters)
        ]
        pip = [
            add_prefix_to_uppercase_input_parameters(b.parsed)
            for b in self.blocks
            if isinstance(b, ProjectInputParameters)
        ]

        substitutes = build_substitutes(
            itertools.chain(*pip), itertools.chain(*dip)
        ) | build_substitutes(itertools.chain(*dcp), itertools.chain(*pcp))

        visitor = FormulaSubstitutor(substitutes)

        for obj in itertools.chain(*dcp):
            substitute_in_formulas(obj, visitor)

        global_params = {o["name"]: o["amount"] for o in itertools.chain(*dip)} | {
            o["name"]: o["amount"] for o in itertools.chain(*pip)
        }

        ps = ParameterSet({o["name"]: o for o in itertools.chain(*dcp)}, global_params)
        parameter_set_evaluate_each_formula(ps)

        substitutes = substitutes | {
            o["original_name"].upper(): o["name"] for o in itertools.chain(*dcp)
        }
        visitor = FormulaSubstitutor(substitutes)
        global_params = global_params | {o["name"]: o["amount"] for o in itertools.chain(*dcp)}

        for obj in itertools.chain(*pcp):
            substitute_in_formulas(obj, visitor)

        ps = ParameterSet({o["name"]: o for o in itertools.chain(*pcp)}, global_params)
        parameter_set_evaluate_each_formula(ps)

        substitutes = substitutes | {
            o["original_name"].upper(): o["name"] for o in itertools.chain(*pcp)
        }
        visitor = FormulaSubstitutor(substitutes)
        global_params = global_params | {o["name"]: o["amount"] for o in itertools.chain(*pcp)}

        logger.info(
            "Extracted and cleaned {n} process datasets",
            n=sum([1 for block in self if isinstance(block, Process)]),
        )
        for block in filter(lambda b: isinstance(b, Process), self):
            block.resolve_local_parameters(global_params=global_params, substitutes=substitutes)
            block.check_waste_production_model_consistency()
            block.supplement_biosphere_edges(blocks=self.blocks)
