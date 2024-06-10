from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.blocks import DamageCategory


def test_impact_category(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "damagecategory.txt")
    pip = [elem.parsed for elem in obj.blocks if isinstance(elem, DamageCategory)]
    assert len(pip) == 2
    assert pip == [{
        'name': 'NORM - Human Health',
        'unit': 'DALY',
        'impact_categories': [{
            'name': 'NORM - HH - Releases',
            'factor': 1.51,
        }]
    }, {
        'name': 'NORM - Ecosystems',
        'unit': 'PDFm3d',
        'impact_categories': [{
            'name': 'NORM - Eco - Freshwater',
            'factor': 0.5
        }, {
            'name': 'NORM - Eco - Marine',
            'factor': 0.5
        }, {
            'name': 'NORM - Eco - Terrestrial',
            'factor': 0.5
        }]
    }]
