from bw_simapro_csv import SimaProCSV
from bw_simapro_csv.blocks import LiteratureReference


def test_literature_references_missing(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "header.csv")
    pip = [elem for elem in obj.blocks if isinstance(elem, LiteratureReference)]
    assert pip == []


def test_literature_references_missing(fixtures_dir):
    obj = SimaProCSV(fixtures_dir / "external_documents_and_literature_references.csv")
    pip = [elem.parsed for elem in obj.blocks if isinstance(elem, LiteratureReference)]
    assert pip == [{
        'Name': 'Ecoinvent 3',
        'Documentation link': 'http://www.ecoinvent.org',
        'Category': 'Ecoinvent',
        'Description': None,
    }, {
        'Name': 'Erdöl/2007/Jungbluth, N.',
        'Documentation link': 'http://www.ecoinvent.org',
        'Category': 'Ecoinvent',
        'Description': 'Jungbluth, N. (2007) Erdöl. Sachbilanzen von Energiesystemen. Final report No. 6 ecoinvent data v2.0. Editors: Dones R.. Volume: 6. Swiss Centre for LCI, PSI. Dübendorf and Villigen, CH.\nType: Measurement on site\nSource: CD-ROM\nFirst author: Jungbluth, N.\nYear: 2007\nName of editors: Dones R.\nTitle of anthology: Sachbilanzen von Energiesystemen. Final report No. 6 ecoinvent data v2.0\nPlace of publication: Dübendorf and Villigen, CH\nPublisher: Swiss Centre for LCI, PSI\nVolume No: 6'
    }, {
        'Name': 'Life Cycle Inventories of Agricultural Production Systems/2007/Nemecek, T.',
        'Documentation link': 'http://www.ecoinvent.org',
        'Category': 'Ecoinvent',
        'Description': 'Nemecek, T., Kägi, T., Blaser, S. (2007) Life Cycle Inventories of Agricultural Production Systems. Ecoinvent report version 2.0. Editors: 0. Volume: 15. Swiss Centre for LCI, ART. Duebendorf and Zurich, CH.\nType: Measurement on site\nSource: CD-ROM\nFirst author: Nemecek, T.\nOther authors: Kägi, T., Blaser, S.\nYear: 2007\nName of editors: 0\nTitle of anthology: Ecoinvent report version 2.0\nPlace of publication: Duebendorf and Zurich, CH\nPublisher: Swiss Centre for LCI, ART\nVolume No: 15',
    }]
