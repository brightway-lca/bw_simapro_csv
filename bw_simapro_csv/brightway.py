import datetime
import itertools
from typing import Union

from loguru import logger

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


def substitute_unspecified(s: Union[str, None]) -> Union[str, None]:
    if s and isinstance(s, str) and s.lower() == "unspecified":
        return None
    return s


def lci_to_brightway(spcsv: SimaProCSV, missing_string: str = "(unknown)") -> dict:
    """Turn an extracted SimaPro CSV extract into metadata that can be imported into Brightway.

    Doesn't do any normalization or other data changes, just reorganizes the existing data."""
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
        "project_parameters": itertools.chain(
            *[
                block.parsed
                for block in spcsv.blocks
                if isinstance(block, (DatabaseCalculatedParameters, DatabaseInputParameters))
            ]
        ),
        "database_parameters": itertools.chain(
            *[
                block.parsed
                for block in spcsv.blocks
                if isinstance(block, (ProjectCalculatedParameters, ProjectInputParameters))
            ]
        ),
    }

    literature_mapping = {
        obj.parsed["Name"]: obj.parsed
        for obj in filter(lambda b: isinstance(b, LiteratureReference), spcsv)
    }

    for process in filter(lambda b: isinstance(b, Process), spcsv):
        process_dataset = {
            "database": spcsv.database_name,
            "simapro_project": substitute_unspecified(spcsv.header["project"]) or missing_string,
            "code": process.parsed["metadata"]["Process identifier"],
            "exchanges": [],
            "type": "multifunctional" if len(process.blocks["Products"].parsed) > 1 else "process",
            "name": substitute_unspecified(process.parsed["metadata"].get("Process name"))
            or missing_string,
            "comment": substitute_unspecified(process.parsed["metadata"].get("Comment"))
            or missing_string,
            "location": substitute_unspecified(process.parsed["metadata"].get("Geography"))
            or missing_string,
            "data_generator": substitute_unspecified(process.parsed["metadata"].get("Generator"))
            or missing_string,
            "data_entry": substitute_unspecified(process.parsed["metadata"].get("Record"))
            or missing_string,
            "data_links": substitute_unspecified(
                process.parsed["metadata"].get("External documents")
            )
            or missing_string,
            "publication_date": process.parsed["metadata"].get("Date") or datetime.date.today(),
            "tags": {},
        }
        if process.parsed["metadata"].get("Literature references"):
            process_dataset["references"] = []
            for reference in process.parsed["metadata"]["Literature references"]:
                if reference["reference"] not in literature_mapping:
                    logger.warning(
                        "Skipping missing reference {r}; not present in given references {g}",
                        r=reference["reference"],
                        g=list(literature_mapping),
                    )
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
            logger.info(AVOIDED_PRODUCTS_WARNING)
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

        data["processes"].append(process_dataset)

    return data