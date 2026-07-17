from app.semantic_layer.semantic_parser import SemanticParser
from app.sql_engine.planner import StructuredQueryPlanner


def plan(query: str):
    semantic = SemanticParser().parse_typed(query)
    return StructuredQueryPlanner().plan(semantic)


def test_metric_lookup():
    result = plan("What was enterprise revenue in APAC in Q4 2025?")
    assert result.specs[0].query_shape == "metric_lookup"


def test_grouped_metric():
    result = plan("Show revenue by region in Q4 2025.")
    assert result.specs[0].query_shape == "grouped_metric"
    assert result.specs[0].dimensions == ["region"]


def test_period_comparison():
    result = plan("Compare APAC enterprise revenue in Q3 and Q4 2025.")
    assert result.specs[0].query_shape == "period_comparison"


def test_absolute_change():
    result = plan("How much did APAC enterprise revenue decline from Q3 to Q4 2025?")
    assert result.specs[0].query_shape == "absolute_change"


def test_percentage_change():
    result = plan("What was the percentage change in APAC enterprise revenue from Q3 to Q4 2025?")
    assert result.specs[0].query_shape == "percentage_change"


def test_multiple_independent_metrics():
    result = plan("Compare revenue and marketing spend in APAC in Q4 2025.")
    assert len(result.specs) == 2


def test_top_n_grouped_metric():
    result = plan("Which regions had the highest revenue in Q4 2025?")
    assert result.specs[0].query_shape == "top_n"


def test_count_query():
    result = plan("How many enterprise customers are in APAC?")
    assert result.specs[0].query_shape == "count_query"


def test_unsupported_semantics_block_planning():
    result = plan("How were sales?")
    assert result.errors
