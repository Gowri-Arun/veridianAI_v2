from app.schemas.sql import CompiledSQLQuery
from app.semantic_layer.semantic_parser import SemanticParser
from app.sql_engine.compiler import SQLCompiler
from app.sql_engine.planner import StructuredQueryPlanner
from app.sql_engine.safety import SQLSafetyValidator


def compile_first(query: str):
    semantic = SemanticParser().parse_typed(query)
    spec = StructuredQueryPlanner().plan(semantic).specs[0]
    return SQLCompiler().compile(spec)


def test_values_are_parameterized():
    compiled = compile_first("What was enterprise revenue in APAC in Q4 2025?")
    assert "APAC" not in compiled.sql
    assert "Enterprise" not in compiled.sql
    assert compiled.parameters == ["APAC", "Enterprise", "Q4_2025"]


def test_grouping_and_ordering():
    compiled = compile_first("Which regions had the highest revenue in Q4 2025?")
    assert "GROUP BY region" in compiled.sql
    assert "ORDER BY revenue DESC" in compiled.sql
    assert "LIMIT 10" in compiled.sql


def test_period_list_parameterized():
    compiled = compile_first("Compare APAC enterprise revenue in Q3 and Q4 2025.")
    assert "quarter IN (?, ?)" in compiled.sql
    assert compiled.parameters[-2:] == ["Q3_2025", "Q4_2025"]


def test_no_raw_query_in_sql():
    compiled = compile_first("What was enterprise revenue in APAC in Q4 2025?")
    assert "What was" not in compiled.sql


def test_safety_rejects_unsafe_sql():
    validator = SQLSafetyValidator()
    unsafe = [
        "DROP TABLE revenue",
        "DELETE FROM customers",
        "UPDATE revenue SET recognized_revenue = 0",
        "SELECT * FROM read_csv_auto('x.csv')",
        "SELECT * FROM parquet_scan('x.parquet')",
        "ATTACH 'x'",
        "INSTALL httpfs",
        "LOAD httpfs",
        "SELECT 1; DROP TABLE revenue",
        "SELECT * FROM revenue -- comment",
    ]
    for sql in unsafe:
        error = validator.validate(CompiledSQLQuery(query_id="x", sql=sql, parameters=[], explanation="test"))
        assert error is not None


def test_safety_allows_compiler_output():
    compiled = compile_first("Show revenue by region in Q4 2025.")
    assert SQLSafetyValidator().validate(compiled) is None
