import datetime

from bw_simapro_csv import SimaProCSV


def test_basic_header_extraction(fixtures_dir):
    given = SimaProCSV(fixtures_dir / "allocation.csv").to_brightway(separate_products=False)
    expected = {
        "created": "2016-10-12T22:54:47",
        "name": "Bobs_burgers",
        "simapro_csv_version": None,
        "simapro_libraries": ["Methods"],
        "simapro_project": "Bobs_burgers",
        "simapro_version": "8.2.0.0",
    }
    for key, value in expected.items():
        assert value == given["database"][key]

    first = given["processes"][0]
    expected = {
        "code": "ReCenter000033915300046",
        "comment": "No soup for you! This is agricultural residues, actually.",
        "name": "Agricultural residues, non-mechanized, sun dried, at farm, 1 kg dry matter (WFLDB 3.0)/GLO U",
    }
    for key, value in expected.items():
        assert first[key] == value

    allocated = given["processes"][1]
    expected = {
        "code": "ReCenter000033915302504",
        "comment": "Stuff happened, and then we enjoyed life outside the office",
        "data_entry": "Some people and stuff like that",
        "data_generator": "Somebody",
        "database": "Bobs_burgers",
        "location": None,
        "mf_strategy_label": "property allocation by 'manual_allocation'",
        "mf_was_once_allocated": True,
        "mf_allocation_run_uuid": allocated["mf_allocation_run_uuid"],
        "name": "MFP: Rice, at farm (WFLDB 3.0)⧺Rice straw, at farm (WFLD",
        "publication_date": datetime.date(2015, 6, 8),
        "references": [],
        "simapro_project": "Bobs_burgers",
        "tags": {
            "category_type": "material",
            "simapro_type": "Unit process",
            "system_description": "ECOSPOLD IMPORT",
        },
        "type": "multifunctional",
    }
    for key, value in expected.items():
        assert allocated[key] == value

    assert set(expected).union({"exchanges"}) == set(allocated)

    expected = {
        "allocation": 95.8,
        "amount": 6250.0,
        "category": r"_WFLDB 3.0\Plant products\Arable\Rice",
        "comment": "INDIA",
        "functional": True,
        "line_no": 208,
        "mf_allocated": True,
        "mf_manual_input_product": False,
        "name": "Rice, at farm (WFLDB 3.0)/IN U",
        "properties": {"manual_allocation": 95.8},
        "type": "production",
        "unit": "kg",
        "waste_type": "not defined",
    }
    for key, value in expected.items():
        assert allocated["exchanges"][0][key] == value

    assert allocated["exchanges"][0]["input"]
    assert allocated["exchanges"][0]["mf_allocated_process_code"]
    assert (
        allocated["exchanges"][0]["input"][1]
        == allocated["exchanges"][0]["mf_allocated_process_code"]
    )

    expected = {
        "allocation": 4.2,
        "amount": 3125.0,
        "category": r"_WFLDB 3.0\Plant products\Arable\Rice",
        "comment": "The amount of straw is calculated "
        "from the straw to grain-ratio of 1 "
        "and a straw harvest rate of 50%. "
        "Economic allocation is based on the "
        "assumption that grains account for "
        "92% and straw for 8% of the price.",
        "functional": True,
        "mf_allocated": True,
        "mf_manual_input_product": False,
        "line_no": 209,
        "name": "Rice straw, at farm (WFLDB 3.0)/IN U",
        "properties": {"manual_allocation": 4.2},
        "type": "production",
        "unit": "kg",
        "waste_type": "not defined",
    }

    for key, value in expected.items():
        assert allocated["exchanges"][1][key] == value

    assert allocated["exchanges"][1]["input"]
    assert allocated["exchanges"][1]["mf_allocated_process_code"]
    assert (
        allocated["exchanges"][1]["input"][1]
        == allocated["exchanges"][1]["mf_allocated_process_code"]
    )
