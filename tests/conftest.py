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
    def temp_user_log_dir(*args, **kwargs):
        return tmp_path

    monkeypatch.setattr(platformdirs, "user_log_dir", temp_user_log_dir)
