from pathlib import Path

import duckdb


WAREHOUSE_PATH = Path("data/warehouse/veridian.duckdb")


def main() -> None:
    con = duckdb.connect(str(WAREHOUSE_PATH), read_only=True)
    try:
        tables = [row[0] for row in con.execute("SHOW TABLES").fetchall()]
        for table in tables:
            columns = con.execute(f"PRAGMA table_info('{table}')").fetchall()
            rendered = ", ".join(f"{col[1]}:{col[2]}" for col in columns)
            print(f"{table}: {rendered}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
