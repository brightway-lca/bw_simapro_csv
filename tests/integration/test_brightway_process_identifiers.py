from bw_simapro_csv import SimaProCSV


def test_irregular_process_identifiers(fixtures_dir):
    given = SimaProCSV(fixtures_dir / "allocation.csv").to_brightway()
    for ds in given["processes"]:
        assert ds["code"] and len(ds["code"]) > 20
