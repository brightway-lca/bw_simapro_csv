from bw_simapro_csv import SimaProCSV


def test_basic_product_creation(fixtures_dir):
    given = SimaProCSV(fixtures_dir / "allocation.csv").to_brightway()

    assert len(given["processes"]) == 4
    assert len(given["products"]) == 3

    residue_process = given["processes"][0]
    expected = {
        "code": "ReCenter000033915300046",
        "name": "Agricultural residues, non-mechanized, sun dried, at farm, 1 kg dry matter (WFLDB 3.0)/GLO U",
        "type": "process",
    }
    for key, value in expected.items():
        assert residue_process[key] == value

    mfp = given["processes"][1]
    expected = {
        "code": "ReCenter000033915302504",
        "name": "MFP: Rice, at farm (WFLDB 3.0)⧺Rice straw, at farm (WFLD",
        "type": "multifunctional",
    }
    for key, value in expected.items():
        assert mfp[key] == value

    rice_process = given["processes"][2]
    expected = {
        "mf_parent_key": ("Bobs_burgers", mfp["code"]),
        "name": "Rice, at farm (WFLDB 3.0)/IN U (read-only process)",
        "reference product": "Rice, at farm (WFLDB 3.0)/IN U",
        "type": "readonly_process",
        "unit": "kg",
    }
    for key, value in expected.items():
        assert rice_process[key] == value

    straw_process = given["processes"][3]
    expected = {
        "comment": "Stuff happened, and then we enjoyed life outside the office",
        "mf_parent_key": ("Bobs_burgers", mfp["code"]),
        "name": "Rice straw, at farm (WFLDB 3.0)/IN U (read-only process)",
        "reference product": "Rice straw, at farm (WFLDB 3.0)/IN U",
        "type": "readonly_process",
    }
    for key, value in expected.items():
        assert straw_process[key] == value

    common = (
        "comment",
        "data_entry",
        "data_generator",
        "database",
        "location",
        "mf_allocation_run_uuid",
        "mf_strategy_label",
        "publication_date",
        "references",
        "tags",
        "simapro_project",
    )
    for label in common:
        assert rice_process[label] == mfp[label]
        assert straw_process[label] == mfp[label]

    residue_product = given["products"][0]
    expected = {
        "comment": residue_process["comment"],
        "database": residue_process["database"],
        "line_no": 100,
        "name": "Agricultural residues, non-mechanized, sun dried, at farm, 1 kg dry matter (WFLDB 3.0)/GLO U",
        "properties": {"manual_allocation": 100.0},
        "simapro_project": residue_process["simapro_project"],
        "tags": residue_process["tags"],
        "type": "product",
        "unit": "kg",
        "waste_type": "Compost",
        "category": "_WFLDB 3.0\\_sub-datasets\\Animal production\\Feed",
        "reference process": (residue_process["database"], residue_process["code"]),
    }
    for key, value in expected.items():
        assert residue_product[key] == value

    expected = {
        "allocation": 100,
        "amount": 1,
        "functional": True,
        "input": (residue_product["database"], residue_product["code"]),
        "type": "production",
        "unit": "kg",
    }

    exc = residue_process["exchanges"][-1]
    for key, value in expected.items():
        assert exc[key] == value

    rice_product = given["products"][1]
    expected = {
        "comment": "INDIA",
        "database": mfp["database"],
        "line_no": 208,
        "name": "Rice, at farm (WFLDB 3.0)/IN U",
        "properties": {"manual_allocation": 95.8},
        "simapro_project": mfp["simapro_project"],
        "tags": mfp["tags"],
        "type": "product",
        "unit": "kg",
        "waste_type": "not defined",
        "category": "_WFLDB 3.0\\Plant products\\Arable\\Rice",
        "reference process": (mfp["database"], mfp["code"]),
    }
    for key, value in expected.items():
        assert rice_product[key] == value

    expected = {
        "allocation": 95.8,
        "amount": 6250,
        "functional": True,
        "input": (rice_product["database"], rice_product["code"]),
        "type": "production",
        "unit": "kg",
    }

    exc = rice_process["exchanges"][-1]
    for key, value in expected.items():
        assert exc[key] == value

    straw_product = given["products"][2]
    expected = {
        "comment": r"The amount of straw is calculated from the straw to grain-ratio of 1 and a straw harvest rate of 50%. Economic allocation is based on the assumption that grains account for 92% and straw for 8% of the price.",
        "database": mfp["database"],
        "line_no": 209,
        "name": "Rice straw, at farm (WFLDB 3.0)/IN U",
        "properties": {"manual_allocation": 4.2},
        "simapro_project": mfp["simapro_project"],
        "tags": mfp["tags"],
        "type": "product",
        "unit": "kg",
        "waste_type": "not defined",
        "category": "_WFLDB 3.0\\Plant products\\Arable\\Rice",
        "reference process": (mfp["database"], mfp["code"]),
    }
    for key, value in expected.items():
        assert straw_product[key] == value

    expected = {
        "allocation": 4.2,
        "amount": 3125,
        "functional": True,
        "input": (straw_product["database"], straw_product["code"]),
        "type": "production",
        "unit": "kg",
    }

    exc = straw_process["exchanges"][-1]
    for key, value in expected.items():
        assert exc[key] == value


def test_no_product_creation(fixtures_dir):
    given = SimaProCSV(fixtures_dir / "allocation.csv").to_brightway(separate_products=False)

    assert len(given["processes"]) == 4
    assert len(given["products"]) == 0
