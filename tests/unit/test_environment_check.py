from pathlib import Path

import scripts.check_environment as check_environment


def test_required_imports_declared():
    assert "duckdb" in check_environment.REQUIRED_IMPORTS
    assert "pydantic" in check_environment.REQUIRED_IMPORTS


def test_repo_root_resolution():
    root = Path(check_environment.__file__).resolve().parents[1]
    assert (root / "app").exists()
    assert (root / "benchmarks").exists()
