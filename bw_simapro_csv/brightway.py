import datetime
import itertools
from copy import deepcopy
from typing import Union
from uuid import uuid4

from loguru import logger
from multifunctional import allocation_before_writing

from .blocks import (
    DatabaseCalculatedParameters,
    DatabaseInputParameters,
    LiteratureReference,
    Process,
    ProjectCalculatedParameters,
    ProjectInputParameters,
)
from .main import SimaProCSV

OPTIONAL_TAG_MAPPING = [
    ("Type", "simapro_type"),
    ("Time period", "time_period"),
    ("Technology", "technology"),
    ("Representativeness", "representativeness"),
    ("Multiple output allocation", "allocation_method"),
    ("Boundary with nature", "ecosphere_boundary"),
    ("Category type", "category_type"),
    ("Substitution allocation", "substitution_method"),
    ("Cut off rules", "cutoff_rules"),
    ("Capital goods", "capital_goods"),
    ("System description", "system_description"),
]
AVOIDED_PRODUCTS_WARNING = """Processing avoided products block.
Please check exchanges with type `substitution` carefully - we don't have data to test this."""
TECHNOSPHERE_EDGES = ("Materials/fuels", "Electricity/heat")
BIOSPHERE_EDGES = (
    "Economic issues",
    "Emissions to air",
    "Emissions to soil",
    "Emissions to water",
    "Final waste flows",
    "Non material emissions",
    "Resources",
    "Social issues",
)
OPTIONAL_PROCESS_FIELDS = [
    ("Comment", "comment"),
    ("Generator", "data_generator"),
    ("Record", "data_entry"),
    ("External documents", "data_links"),
    ("Collection method", "collection_method"),
    ("Verification", "verification"),
    ("Allocation rules", "allocation_rules"),
]


def substitute_unspecified(s: Union[str, None]) -> Union[str, None]:
    if s and isinstance(s, str) and s.lower() == "unspecified":
        return None
    return s


def allocation_as_manual_property(exc: dict) -> dict:
    """If allocation field is present, add it as manual property as well"""
    if "allocation" in exc:
        if "properties" not in exc:
            exc["properties"] = {}
        exc["properties"]["manual_allocation"] = exc["allocation"]
    return exc


def name_for_process(process: Process, missing_string: str, shorten_names: bool = True) -> str:
    """Try several ways to generate a sensible name."""

    def clean_name(name: str) -> str:
        """Cleanup awkward name endings if needed."""
        name = name.strip()
        if name.endswith(","):
            name = name[:-1]
        return name

    if given_name := substitute_unspecified(process.parsed["metadata"].get("Process name")):
        return given_name
    if "Products" in process.blocks:
        names = [edge["name"] for edge in process.blocks["Products"].parsed]
        if len(names) == 1:
            return names[0]
        else:
            return clean_name(
                "MFP: {}".format(
                    "⧺".join([(name[:25] if shorten_names else name) for name in names])
                )
            )
    if "Waste treatment" in process.blocks:
        names = [edge["name"] for edge in process.blocks["Waste treatment"].parsed]
        if len(names) == 1:
            return names[0]
        else:
            return clean_name(
                "MFP: {}".format(
                    "⧺".join([(name[:25] if shorten_names else name) for name in names])
                )
            )
    return missing_string


def as_product_dct(edge: dict, node: dict) -> dict:
    """Take an edge on a node and generate a new product node."""
    NODE_ATTRS = ("name", "unit", "simapro_project", "location", "tags", "database", "comment")
    EDGE_ATTRS = (
        "name",
        "unit",
        "line_no",
        "category",
        "waste_type",
        "comment",
        "properties",
        "simapro_category",
    )
    return (
        {
            "type": "product",
            "code": uuid4().hex,
            "reference process": (node["database"], node["code"]),
        }
        | {key: node[key] for key in NODE_ATTRS if node.get(key)}
        | {key: edge[key] for key in EDGE_ATTRS if edge.get(key)}
    )


def reference_to_product(process_edge: dict, product: dict) -> dict:
    """Add explicit link from process edge to new product node"""
    process_edge["input"] = (product["database"], product["code"])
    return process_edge


def lci_to_brightway(
    spcsv: SimaProCSV,
    missing_string: str = "(unknown)",
    separate_products: bool = False,
    shorten_names: bool = True,
) -> dict:
    """Turn an extracted SimaPro CSV extract into metadata that can be imported into Brightway.

    Doesn't do any normalization or other data changes, just reorganizes the existing data."""
    issued_warnings = set()

    data = {
        "database": {
            "name": spcsv.database_name,
            "simapro_filepath": spcsv.filepath,
            "simapro_project": spcsv.header.get("project"),
            "simapro_libraries": spcsv.header.get("libraries"),
            "simapro_version": spcsv.header.get("simapro_version"),
            "simapro_csv_version": spcsv.header.get("simapro_csv_version"),
            "created": spcsv.header["created"].isoformat()[:19],
        },
        "processes": [],
        # Note reversing of database and project terms here
        # In SimaPro, the project is lower priority than the database
        # but in Brightway it's the opposite.
        "products": [],
        "project_parameters": [
            param
            for block in spcsv.blocks
            for param in block.parsed
            if isinstance(block, (DatabaseCalculatedParameters, DatabaseInputParameters))
        ],
        "database_parameters": [
            param
            for block in spcsv.blocks
            for param in block.parsed
            if isinstance(block, (ProjectCalculatedParameters, ProjectInputParameters))
        ],
    }

    literature_mapping = {
        obj.parsed["Name"]: obj.parsed
        for obj in filter(lambda b: isinstance(b, LiteratureReference), spcsv)
    }

    known_missing_references = set()

    for process in filter(lambda b: isinstance(b, Process), spcsv):
        multifunctional = (
            len(process.blocks.get("Products", [])) + len(process.blocks.get("Waste treatment", []))
        ) > 1

        code = process.parsed["metadata"].get("Process identifier")
        if not code or not code.strip() or code.strip() in {'""', "''"}:
            code = uuid4().hex

        process_dataset = {
            "database": spcsv.database_name,
            "simapro_project": substitute_unspecified(spcsv.header["project"]) or missing_string,
            "code": code,
            "exchanges": [],
            "type": "multifunctional" if multifunctional else "process",
            "name": name_for_process(process, missing_string, shorten_names),
            "location": substitute_unspecified(process.parsed["metadata"].get("Geography")),
            "publication_date": (
                process.parsed["metadata"].get("Date") or datetime.date.today()
            ).isoformat()[:19],
            "tags": {},
        }

        for sp_label, bw_label in OPTIONAL_PROCESS_FIELDS:
            if val := substitute_unspecified(process.parsed["metadata"].get(sp_label)):
                process_dataset[bw_label] = val

        if process.parsed["metadata"].get("Literature references"):
            process_dataset["references"] = []
            for reference in process.parsed["metadata"]["Literature references"]:
                if reference["reference"] in known_missing_references:
                    continue
                elif reference["reference"] not in literature_mapping:
                    logger.warning(
                        "Skipping missing reference {r}; not present in given references {g}",
                        r=reference["reference"],
                        g=list(literature_mapping),
                    )
                    known_missing_references.add(reference["reference"])
                else:
                    literature = literature_mapping[reference["reference"]]
                    process_dataset["references"].append(
                        {
                            "year": substitute_unspecified(literature.get("Year"))
                            or missing_string,
                            "authors": substitute_unspecified(literature.get("Authors"))
                            or missing_string,
                            "comment": substitute_unspecified(reference.get("comment"))
                            or missing_string,
                        }
                        | {
                            k.lower().replace(" ", "_"): v
                            for k, v in literature.items()
                            if k != "Name" and v
                        }
                    )
        for tag_in, tag_out in OPTIONAL_TAG_MAPPING:
            if tag_in in process.parsed["metadata"] and substitute_unspecified(
                process.parsed["metadata"][tag_in]
            ):
                process_dataset["tags"][tag_out] = process.parsed["metadata"][tag_in]

        if "Avoided products" in process.blocks:
            if AVOIDED_PRODUCTS_WARNING not in issued_warnings:
                logger.info(AVOIDED_PRODUCTS_WARNING)
                issued_warnings.add(AVOIDED_PRODUCTS_WARNING)
            for edge in process.blocks["Avoided products"].parsed:
                process_dataset["exchanges"].append(
                    edge | {"type": "substitution", "functional": False}
                )
        if "Waste to treatment" in process.blocks:
            for edge in process.blocks["Waste to treatment"].parsed:
                process_dataset["exchanges"].append(
                    edge | {"type": "production", "functional": False}
                )
        for label in TECHNOSPHERE_EDGES:
            if label in process.blocks:
                for edge in process.blocks[label].parsed:
                    process_dataset["exchanges"].append(
                        edge | {"type": "technosphere", "simapro_category": label}
                    )
        for label in BIOSPHERE_EDGES:
            if label in process.blocks:
                for edge in process.blocks[label].parsed:
                    process_dataset["exchanges"].append(edge | {"type": "biosphere"})
        if "Products" in process.blocks:
            for edge in process.blocks["Products"].parsed:
                production_dct = allocation_as_manual_property(
                    edge | {"type": "production", "functional": True}
                )
                if separate_products:
                    product_dct = as_product_dct(production_dct, process_dataset)
                    data["products"].append(product_dct)
                    process_dataset["exchanges"].append(
                        reference_to_product(production_dct, product_dct)
                    )
                else:
                    process_dataset["exchanges"].append(production_dct)
        elif "Waste treatment" in process.blocks:
            for edge in process.blocks["Waste treatment"].parsed:
                waste_edge = edge | {"type": "technosphere", "functional": True}
                if separate_products:
                    waste_dct = as_product_dct(waste_edge, process_dataset)
                    data["products"].append(waste_dct)
                    process_dataset["exchanges"].append(reference_to_product(waste_edge, waste_dct))
                else:
                    process_dataset["exchanges"].append(waste_edge)
                if not any(e for e in process_dataset["exchanges"] if e["type"] == "production"):
                    dummy = deepcopy(edge)
                    dummy.update(
                        {
                            "amount": 0,
                            "type": "production",
                            "functional": False,
                            "comment": "Dummy edge inserted to stop auto-generation of unitary production edge",
                        }
                    )
                    process_dataset["exchanges"].append(dummy)

        data["processes"].append(process_dataset)

    if any(
        sum(1 for exc in ds.get("exchanges") if exc.get("functional")) > 1
        for ds in data["processes"]
    ):
        as_dict = allocation_before_writing(
            {(spcsv.database_name, ds["code"]): ds for ds in data["processes"]}, "manual_allocation"
        )
        for (database, code), ds in as_dict.items():
            ds["code"] = code
            ds["database"] = database
        data["processes"] = list(as_dict.values())

    return data
