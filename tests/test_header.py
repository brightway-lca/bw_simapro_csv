from datetime import datetime
from pathlib import Path

import pytest

from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.header import SimaProCSVType, parse_header


def test_log_file_patching(fixtures_dir: Path, temporary_logs_dir: Path):
    obj = SimaProCSV(fixtures_dir / "allocation.csv")
    assert str(temporary_logs_dir) in str(obj.logs_dir)


def test_basic_header_extraction(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "allocation.csv")
    assert obj.header == {
        "simapro_version": "8.2.0.0",
        "kind": SimaProCSVType.processes,
        "delimiter": ";",
        "project": "Bobs_burgers",
        "csv_version": "8.0.5",
        "libraries": ["Methods"],
        "dayfirst": False,
        "selection": "Selection (2)",
        "open_project": "Bobs_burgers",
        "exclude_library_processes": None,
        "open_library": None,
        "date_separator": "/",
        "export_platform_ids": None,
        "skip_empty_fields": False,
        "convert_expressions": True,
        "related_objects": True,
        "include_stages": True,
        "decimal_separator": ".",
        "created": datetime(2016, 10, 12, 22, 54, 47),
    }

    obj = SimaProCSV(fixtures_dir / "damagecategory.txt")
    assert obj.header == {
        "simapro_version": "8.2.0.0",
        "kind": SimaProCSVType.methods,
        "delimiter": "\t",
        "project": "DC Test",
        "csv_version": "8.0.5",
        "libraries": [],
        "dayfirst": True,
        "selection": "Current (1)",
        "open_project": None,
        "exclude_library_processes": None,
        "open_library": None,
        "date_separator": "/",
        "export_platform_ids": None,
        "skip_empty_fields": None,
        "convert_expressions": None,
        "related_objects": True,
        "include_stages": False,
        "decimal_separator": ".",
        "created": datetime(2017, 2, 6, 19, 30, 50),
    }

    obj = SimaProCSV(fixtures_dir / "external_documents_and_literature_references.csv")
    assert obj.header == {
        "simapro_version": "9.3.0.3",
        "kind": SimaProCSVType.processes,
        "delimiter": ";",
        "project": "Dummy project",
        "csv_version": "9.0.0",
        "libraries": ["AGRIBALYSE 3", "Methods", "World Food LCA Database"],
        "dayfirst": True,
        "selection": "Current (1)",
        "open_project": "Dummy project",
        "exclude_library_processes": None,
        "open_library": None,
        "date_separator": "/",
        "export_platform_ids": False,
        "skip_empty_fields": False,
        "convert_expressions": True,
        "related_objects": True,
        "include_stages": True,
        "decimal_separator": ".",
        "created": datetime(2022, 9, 27, 8, 54, 29),
    }

    # Header can also have delimiter-separated values
    obj = SimaProCSV(fixtures_dir / "header.csv")
    assert obj.header == {
        "simapro_version": "8.5.0.0",
        "kind": SimaProCSVType.methods,
        "delimiter": ";",
        "project": "Methods",
        "csv_version": "8.0.5",
        "libraries": [],
        "dayfirst": False,
        "selection": "Selection (1)",
        "exclude_library_processes": None,
        "open_project": None,
        "open_library": "Methods",
        "date_separator": "-",
        "export_platform_ids": None,
        "skip_empty_fields": None,
        "convert_expressions": None,
        "related_objects": True,
        "include_stages": False,
        "decimal_separator": ".",
        "created": datetime(2019, 10, 24, 18, 35, 10),
    }

    obj = SimaProCSV(fixtures_dir / "method_end.csv")
    assert obj.header == {
        "simapro_version": "9.1.0.7",
        "kind": SimaProCSVType.methods,
        "delimiter": ";",
        "project": None,
        "csv_version": "9.0.0",
        "libraries": [],
        "dayfirst": True,
        "exclude_library_processes": None,
        "selection": None,
        "open_project": None,
        "open_library": None,
        "date_separator": ".",
        "export_platform_ids": None,
        "skip_empty_fields": None,
        "convert_expressions": None,
        "related_objects": None,
        "include_stages": None,
        "decimal_separator": ".",
        "created": datetime(2022, 4, 13, 10, 37, 26),
    }

    # obj = SimaProCSV(fixtures_dir / "stages.csv")
    # assert obj.header == {
    #     "simapro_version": "9.1.0.7",
    #     "kind": SimaProCSVType.stages,
    #     "delimiter": ";",
    #     "project": "all stages",
    #     "csv_version": "9.0.0",
    #     "libraries": [],
    #     "dayfirst": True,
    #     "selection": "Selection (5)",
    #     "open_project": "all stages",
    #     "open_library": None,
    #     "date_separator": ".",
    #     "export_platform_ids": True,
    #     "skip_empty_fields": False,
    #     "convert_expressions": False,
    #     "related_objects": True,
    #     "include_stages": True,
    #     "decimal_separator": ".",
    #     "created": datetime(2021, 10, 13, 13, 6, 4),
    # }

    obj = SimaProCSV(fixtures_dir / "waste_scenario.csv")
    assert obj.header == {
        "simapro_version": "9.1.0.7",
        "kind": SimaProCSVType.processes,
        "delimiter": ";",
        "project": "AP9 pilot",
        "csv_version": "9.0.0",
        "libraries": [
            "Ecoinvent 3 - allocation at point of substitution - system",
            "Ecoinvent 3 - allocation at point of substitution - unit",
            "ELCD",
        ],
        "dayfirst": False,
        "selection": "Selection (1)",
        "open_project": "AP9 pilot",
        "exclude_library_processes": None,
        "open_library": None,
        "date_separator": "/",
        "export_platform_ids": True,
        "skip_empty_fields": True,
        "convert_expressions": False,
        "related_objects": True,
        "include_stages": True,
        "decimal_separator": ".",
        "created": datetime(2021, 11, 18, 13, 49, 13),
    }


def test_header_project_missing(fixtures_dir):
    with pytest.raises(ValueError):
        SimaProCSV(fixtures_dir / "missing-project.csv")

    assert SimaProCSV(fixtures_dir / "missing-project.csv", database_name="foo")


def test_minimal_header_extraction(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "minimal_header.csv")
    assert obj.header == {
        "simapro_version": "9.5.0.2",
        "kind": SimaProCSVType.processes,
        "delimiter": ";",
        "project": "foo_bar",
        "csv_version": "9.0.0",
        "libraries": [],
        "dayfirst": False,
        "date_separator": "/",
        "open_project": None,
        "exclude_library_processes": None,
        "open_library": None,
        "export_platform_ids": None,
        "skip_empty_fields": None,
        "convert_expressions": None,
        "selection": None,
        "related_objects": None,
        "include_stages": None,
        "decimal_separator": ".",
        "created": datetime(2024, 2, 20, 14, 42, 45),
    }


def test_header_without_date():
    given = [
        "{SimaPro 1.2.3.4}",
        "{product stages}",
        "{CSV separator: &}",
        "{Short date format: yyyy-MM-dd}",
        "{CSV Format version: 1.2}",
    ]
    result = parse_header(given)[0].model_dump()
    expected = {
        "csv_version": "1.2",
        "date_separator": "/",
        "dayfirst": True,
        "decimal_separator": ".",
        "delimiter": "&",
        "kind": "product stages",
        "libraries": [],
        "simapro_version": "1.2.3.4",
    }
    for k, v in expected.items():
        assert result[k] == expected[k]
    assert result["created"].year >= 2024
