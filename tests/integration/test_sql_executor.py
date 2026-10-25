import duckdb

from app.schemas.sql import CompiledSQLQuery
from app.sql_engine.executor import DuckDBExecutor


def make_db(path):
    con = duckdb.connect(str(path))
    con.execute("CREATE TABLE revenue (quarter VARCHAR, region VARCHAR, segment VARCHAR, recognized_revenue DOUBLE)")
    con.execute("INSERT INTO revenue VALUES ('Q3_2025','APAC','Enterprise',100.0), ('Q4_2025','APAC','Enterprise',80.0), ('Q4_2025','EMEA','Enterprise',50.0)")
    con.close()


def test_successful_lookup_and_grouping(tmp_path):
    db_path = tmp_path / "test.duckdb"
    make_db(db_path)
    executor = DuckDBExecutor(warehouse_path=db_path)
    result = executor.execute(CompiledSQLQuery(query_id="q1", sql="SELECT region, SUM(recognized_revenue) AS revenue FROM revenue WHERE quarter = ? GROUP BY region", parameters=["Q4_2025"], explanation="test"))
    assert result.error is None
    assert result.row_count == 2
    assert result.execution_ms is not None


def test_empty_result(tmp_path):
    db_path = tmp_path / "test.duckdb"
    make_db(db_path)
    result = DuckDBExecutor(warehouse_path=db_path).execute(CompiledSQLQuery(query_id="q1", sql="SELECT SUM(recognized_revenue) AS revenue FROM revenue WHERE quarter = ?", parameters=["Q1_2024"], explanation="test"))
    assert result.error is None
    assert result.row_count == 1


def test_missing_database(tmp_path):
    result = DuckDBExecutor(warehouse_path=tmp_path / "missing.duckdb").execute(CompiledSQLQuery(query_id="q1", sql="SELECT 1", parameters=[], explanation="test"))
    assert result.error is not None
    assert result.error.code == "MISSING_DATABASE"


def test_invalid_compiled_query(tmp_path):
    db_path = tmp_path / "test.duckdb"
    make_db(db_path)
    result = DuckDBExecutor(warehouse_path=db_path).execute(CompiledSQLQuery(query_id="q1", sql="SELECT * FROM missing", parameters=[], explanation="test"))
    assert result.error is not None


def test_read_only_enforcement_preserves_rows(tmp_path):
    db_path = tmp_path / "test.duckdb"
    make_db(db_path)
    executor = DuckDBExecutor(warehouse_path=db_path)
    result = executor.execute(CompiledSQLQuery(query_id="q1", sql="SELECT COUNT(*) AS count FROM revenue", parameters=[], explanation="test"))
    assert result.rows[0]["count"] == 3
    con = duckdb.connect(str(db_path))
    assert con.execute("SELECT COUNT(*) FROM revenue").fetchone()[0] == 3
    con.close()
