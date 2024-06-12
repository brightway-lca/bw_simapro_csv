import datetime
from pprint import pprint

from bw_simapro_csv import SimaProCSV, SimaProCSVType
from bw_simapro_csv.blocks import SimaProCSVBlock


def test_basic_header_extraction(fixtures_dir):
    given = SimaProCSV(fixtures_dir / "process.csv")
    expected = [1, 2, 3]

    expected_header = {
        "convert_expressions": None,
        "created": datetime.datetime(2014, 3, 7, 15, 52, 27),
        "csv_version": "7.0.0",
        "date_separator": ".",
        "dayfirst": True,
        "decimal_separator": ",",
        "delimiter": ";",
        "export_platform_ids": None,
        "include_stages": None,
        "kind": SimaProCSVType.processes,
        "libraries": [],
        "open_library": None,
        "open_project": None,
        "project": "Test",
        "related_objects": None,
        "selection": None,
        "simapro_version": "8.0",
        "skip_empty_fields": None,
    }
    assert given.header == expected_header

    # for a, b in zip(given, expected):
    #     pprint(a.parsed)
    #     assert a == b
