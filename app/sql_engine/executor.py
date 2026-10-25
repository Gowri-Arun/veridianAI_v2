import time
from pathlib import Path

import duckdb

from app.schemas.sql import CompiledSQLQuery, SQLExecutionError, SQLExecutionResult


DEFAULT_WAREHOUSE_PATH = Path("data/warehouse/veridian.duckdb")


class DuckDBExecutor:
    def __init__(self, warehouse_path: Path = DEFAULT_WAREHOUSE_PATH, max_rows: int = 100):
        self.warehouse_path = warehouse_path
        self.max_rows = max_rows

    def execute(self, compiled: CompiledSQLQuery) -> SQLExecutionResult:
        if not self.warehouse_path.exists():
            return SQLExecutionResult(
                query_id=compiled.query_id,
                error=SQLExecutionError(code="MISSING_DATABASE", message="Warehouse database is missing."),
            )
        started = time.perf_counter()
        try:
            con = duckdb.connect(str(self.warehouse_path), read_only=True)
            try:
                cursor = con.execute(compiled.sql, compiled.parameters)
                columns = [desc[0] for desc in cursor.description]
                tuples = cursor.fetchmany(self.max_rows + 1)
            finally:
                con.close()
            warnings = []
            if len(tuples) > self.max_rows:
                tuples = tuples[: self.max_rows]
                warnings.append(f"Result truncated to {self.max_rows} rows.")
            rows = [dict(zip(columns, row)) for row in tuples]
            elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
            return SQLExecutionResult(
                query_id=compiled.query_id,
                columns=columns,
                rows=rows,
                row_count=len(rows),
                execution_ms=elapsed_ms,
                warnings=warnings,
            )
        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
            return SQLExecutionResult(
                query_id=compiled.query_id,
                execution_ms=elapsed_ms,
                error=SQLExecutionError(code="EXECUTION_FAILED", message="SQL execution failed.", details={"error_type": type(exc).__name__}),
            )
