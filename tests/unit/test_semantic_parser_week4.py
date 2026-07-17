from app.semantic_layer.semantic_parser import SemanticParser


def parse(text: str):
    return SemanticParser().parse_typed(text)


def test_revenue_query():
    result = parse("What was enterprise revenue in APAC in Q4 2025?")
    assert [m.canonical_name for m in result.metrics] == ["revenue"]
    assert {f.dimension: f.value for f in result.filters}["region"] == "APAC"
    assert result.time_range.periods == ["Q4_2025"]


def test_marketing_spend_query():
    result = parse("marketing spend in EMEA in Q4 2025")
    assert result.metrics[0].canonical_name == "marketing_spend"


def test_customer_count_query():
    result = parse("How many enterprise customers are in APAC?")
    assert result.metrics[0].canonical_name == "customer_count"
    assert result.aggregation == "count"


def test_grouped_region_query():
    result = parse("Show revenue by region in Q4 2025.")
    assert any(d.canonical_name == "region" for d in result.dimensions)


def test_multiple_metrics_and_comparison():
    result = parse("Compare revenue and marketing spend in APAC in Q4 2025.")
    assert {m.canonical_name for m in result.metrics} == {"revenue", "marketing_spend"}


def test_percentage_change_detection():
    result = parse("What was the percentage change in APAC enterprise revenue from Q3 to Q4 2025?")
    assert result.comparison.comparison_type == "percentage_change"


def test_ambiguous_sales_query():
    result = parse("How were sales?")
    assert result.requires_clarification is True
    assert result.ambiguities[0].source_term == "sales"


def test_unknown_metric():
    result = parse("What was lunar velocity in Atlantis?")
    assert any(error.code == "UNKNOWN_METRIC" for error in result.errors)


def test_invalid_metric_dimension_combination():
    result = parse("Show marketing spend by segment in Q4 2025.")
    assert any(error.code == "INVALID_DIMENSION_FOR_METRIC" for error in result.errors)


def test_unsupported_aggregation():
    result = parse("Count revenue in Q4 2025.")
    assert any(error.code == "UNSUPPORTED_AGGREGATION" for error in result.errors)
