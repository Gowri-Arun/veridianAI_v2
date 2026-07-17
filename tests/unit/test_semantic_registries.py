import pytest

from app.semantic_layer.dimension_registry import dimension_synonym_lookup, get_dimension
from app.semantic_layer.metric_registry import get_metric, metric_synonym_lookup
from app.semantic_layer.schema_registry import WAREHOUSE_SCHEMA


def test_metric_lookup_and_mapping():
    metric = get_metric("revenue")
    assert metric is not None
    assert metric.source_table == "revenue"
    assert metric.value_column == "recognized_revenue"
    assert "region" in metric.valid_dimensions


def test_metric_synonym_lookup():
    lookup = metric_synonym_lookup()
    assert lookup["recognized revenue"] == "revenue"
    assert lookup["marketing spend"] == "marketing_spend"


def test_dimension_lookup():
    dimension = get_dimension("region")
    assert dimension is not None
    assert "APAC" in dimension.allowed_values
    assert "revenue" in dimension.compatible_metrics


def test_schema_registry_trusted_identifiers():
    assert WAREHOUSE_SCHEMA.has_table("revenue")
    assert WAREHOUSE_SCHEMA.has_column("revenue", "recognized_revenue")
    assert not WAREHOUSE_SCHEMA.has_column("revenue", "not_real")
    assert WAREHOUSE_SCHEMA.joins_allowed is False


def test_forbidden_confusions():
    metric = get_metric("revenue")
    assert metric is not None
    assert "pipeline" in metric.forbidden_confusions


def test_no_duplicate_metric_synonyms():
    lookup = metric_synonym_lookup()
    assert len(lookup) == len(set(lookup.keys()))


def test_unknown_metric_and_dimension():
    assert get_metric("lunar_velocity") is None
    assert get_dimension("planet") is None


def test_dimension_synonym_lookup():
    lookup = dimension_synonym_lookup()
    assert lookup["region"] == "region"
    assert lookup["enterprise"] == "segment"
