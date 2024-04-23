from datetime import datetime

from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.header import SimaProCSVHeader, SimaProCSVType


def test_basic_header_extraction(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "allocation.csv")
    assert obj.header == SimaProCSVHeader(
        simapro_version="8.2.0.0",
        kind=SimaProCSVType.processes,
        delimiter=";",
        project="Bobs_burgers",
        csv_version="8.0.5",
        libraries=["Methods"],
        selection="Selection (2)",
        open_project="Bobs_burgers",
        date_separator="/",
        export_platform_ids=None,
        skip_empty_fields=False,
        convert_expressions=True,
        related_objects=True,
        include_stages=True,
        decimal_separator=".",
        created=datetime(2016, 12, 10, 22, 54, 47),
    )

    obj = SimaProCSV(fixtures_dir / "damagecategory.txt")
    assert obj.header == SimaProCSVHeader(
        simapro_version="8.2.0.0",
        kind=SimaProCSVType.methods,
        delimiter="\t",
        project="DC Test",
        csv_version="8.0.5",
        libraries=[],
        selection="Current (1)",
        open_project="",
        date_separator="/",
        export_platform_ids=None,
        skip_empty_fields=None,
        convert_expressions=None,
        related_objects=True,
        include_stages=False,
        decimal_separator=".",
        created=datetime(2017, 2, 6, 19, 30, 50),
    )

    obj = SimaProCSV(fixtures_dir / "external_documents_and_literature_references.csv")
    assert obj.header == SimaProCSVHeader(
        simapro_version="9.3.0.3",
        kind=SimaProCSVType.processes,
        delimiter=";",
        project="Dummy project",
        csv_version="9.0.0",
        libraries=["AGRIBALYSE 3", "Methods", "World Food LCA Database"],
        selection="Current (1)",
        open_project="Dummy project",
        date_separator="/",
        export_platform_ids=False,
        skip_empty_fields=False,
        convert_expressions=True,
        related_objects=True,
        include_stages=True,
        decimal_separator=".",
        created=datetime(2022, 9, 27, 8, 54, 29),
    )
