import json

import pytest

from scripts.validate_sql_benchmark import BenchmarkValidationError, load_cases


def write_case(path, case):
    path.write_text(json.dumps(case) + "\n", encoding="utf-8")


BASE = {
    "id": "sql_test",
    "question": "What was enterprise revenue in APAC in Q4 2025?",
    "category": "metric_lookup",
    "expected_behavior": "execute",
    "expected_query_shape": "metric_lookup",
    "expected_metrics": ["revenue"],
    "expected_tables": ["revenue"],
    "expected_value_columns": ["recognized_revenue"],
    "expected_filters": {"region": "APAC"},
    "expected_periods": ["Q4_2025"],
    "expected_aggregation": "sum",
    "must_execute_sql": True,
    "difficulty": "easy",
}


def test_valid_case(tmp_path):
    path = tmp_path / "gold.jsonl"
    write_case(path, BASE)
    assert len(load_cases(path)) == 1


def test_duplicate_id(tmp_path):
    path = tmp_path / "gold.jsonl"
    path.write_text(json.dumps(BASE) + "\n" + json.dumps(BASE) + "\n", encoding="utf-8")
    with pytest.raises(BenchmarkValidationError):
        load_cases(path)


def test_malformed_json(tmp_path):
    path = tmp_path / "gold.jsonl"
    path.write_text("{bad\n", encoding="utf-8")
    with pytest.raises(BenchmarkValidationError):
        load_cases(path)


@pytest.mark.parametrize(
    "field,value",
    [
        ("expected_metrics", ["not_real"]),
        ("expected_tables", ["not_real"]),
        ("expected_value_columns", ["not_real"]),
        ("expected_periods", ["Q9_2025"]),
        ("category", "not_real"),
    ],
)
def test_invalid_fields(tmp_path, field, value):
    path = tmp_path / "gold.jsonl"
    case = dict(BASE)
    case[field] = value
    write_case(path, case)
    with pytest.raises((BenchmarkValidationError, ValueError)):
        load_cases(path)


def test_contradictory_execute_reject(tmp_path):
    path = tmp_path / "gold.jsonl"
    case = dict(BASE)
    case["expected_behavior"] = "reject"
    write_case(path, case)
    with pytest.raises(BenchmarkValidationError):
        load_cases(path)
