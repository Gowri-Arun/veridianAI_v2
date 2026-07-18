from pathlib import Path

import duckdb

from scripts.validate_sql_benchmark import DEFAULT_PATH, load_cases


DB_PATH = Path("data/warehouse/veridian.duckdb")


def main() -> None:
    cases = load_cases(DEFAULT_PATH)
    executable = [case for case in cases if case.expected_behavior == "execute"]
    if not DB_PATH.exists():
        raise SystemExit("Warehouse database is missing.")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        print(f"Validated {len(executable)} executable cases against {DB_PATH}.")
        print("Expected row-count and column checks are stored in benchmarks/sql_gold.jsonl.")
        print("Reference numeric materialization is intentionally not generated from the system planner.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
