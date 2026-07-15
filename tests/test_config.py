from pathlib import Path
import sys


sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app import config


def test_relative_db_path_is_resolved_from_project_root(monkeypatch, tmp_path):
    monkeypatch.setenv("DB_PATH", "var/test.db")
    monkeypatch.chdir(tmp_path)

    database_url = config.get_database_url()

    expected_path = (config.PROJECT_ROOT / "var" / "test.db").resolve().as_posix()
    assert database_url == f"sqlite:///{expected_path}"


def test_absolute_db_path_is_preserved(monkeypatch, tmp_path):
    database_path = tmp_path / "persistent" / "test.db"
    monkeypatch.setenv("DB_PATH", str(database_path))

    database_url = config.get_database_url()

    assert database_url == f"sqlite:///{database_path.resolve().as_posix()}"
