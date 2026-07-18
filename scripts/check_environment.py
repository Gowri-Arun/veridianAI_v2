import importlib
import os
from pathlib import Path
import subprocess
import sys


REQUIRED_IMPORTS = ["fastapi", "pydantic", "duckdb", "pandas", "yaml", "pytest", "streamlit", "uvicorn"]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    print(f"python_executable={sys.executable}")
    print(f"python_version={sys.version.split()[0]}")
    print(f"cwd={Path.cwd()}")
    print(f"repo_root={root}")
    print(f"virtual_env={os.environ.get('VIRTUAL_ENV', '')}")
    try:
        pip_version = subprocess.check_output([sys.executable, "-m", "pip", "--version"], text=True).strip()
    except Exception as exc:
        raise SystemExit(f"pip check failed: {exc}")
    print(f"pip={pip_version}")
    for module_name in REQUIRED_IMPORTS:
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, "__version__", "unknown")
            print(f"import {module_name}=ok version={version}")
        except Exception as exc:
            raise SystemExit(f"required import failed: {module_name}: {exc}")
    required_paths = [
        root / "data/warehouse/veridian.duckdb",
        root / "data/processed/document_chunks.jsonl",
        root / "benchmarks/retrieval_gold.jsonl",
        root / "benchmarks/sql_gold.jsonl",
        root / "experiments/results",
        root / "reports",
    ]
    for path in required_paths:
        if path.suffix:
            if not path.exists():
                raise SystemExit(f"required artifact missing: {path}")
        else:
            path.mkdir(parents=True, exist_ok=True)
            test_file = path / ".write_check"
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink()
        print(f"path ok: {path}")
    print("environment-ok")


if __name__ == "__main__":
    main()
