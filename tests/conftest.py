"""Fixtures for bw_simapro_csv"""

from pathlib import Path

import platformdirs
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture(autouse=True)
def temporary_logs_dir(monkeypatch, tmp_path):
    monkeypatch.setattr("bw_simapro_csv.main.user_log_dir", lambda *args, **kwargs: tmp_path)
    yield tmp_path
