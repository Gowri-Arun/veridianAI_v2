import argparse
import json
from pathlib import Path

from pydantic import ValidationError

from app.schemas.benchmark import SQLBenchmarkCase
from app.semantic_layer.dimension_registry import get_dimension
from app.semantic_layer.metric_registry import get_metric
from app.semantic_layer.schema_registry import WAREHOUSE_SCHEMA
from app.semantic_layer.time_normalizer import QUARTERS


DEFAULT_PATH = Path("benchmarks/sql_gold.jsonl")


class BenchmarkValidationError(Exception):
    pass


def load_cases(path: Path = DEFAULT_PATH) -> list[SQLBenchmarkCase]:
    cases: list[SQLBenchmarkCase] = []
    seen: set[str] = set()
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                case = SQLBenchmarkCase(**raw)
            except json.JSONDecodeError as exc:
                raise BenchmarkValidationError(f"line {line_no}: malformed JSON: {exc}") from exc
            except ValidationError as exc:
                raise BenchmarkValidationError(f"line {line_no}: schema validation failed: {exc}") from exc
            if case.id in seen:
                raise BenchmarkValidationError(f"line {line_no}: duplicate id {case.id}")
            seen.add(case.id)
            _validate_case(case, line_no)
            cases.append(case)
    if not cases:
        raise BenchmarkValidationError("benchmark is empty")
    return cases


def _validate_case(case: SQLBenchmarkCase, line_no: int) -> None:
    if case.expected_behavior == "execute" and not case.must_execute_sql:
        raise BenchmarkValidationError(f"line {line_no}: executable cases must set must_execute_sql=true")
    if case.expected_behavior != "execute" and case.must_execute_sql:
        raise BenchmarkValidationError(f"line {line_no}: non-executable cases must not require SQL")
    for metric in case.expected_metrics:
        if not get_metric(metric):
            raise BenchmarkValidationError(f"line {line_no}: unknown metric {metric}")
    for table in case.expected_tables:
        if not WAREHOUSE_SCHEMA.has_table(table):
            raise BenchmarkValidationError(f"line {line_no}: unknown table {table}")
    for table, column in zip(case.expected_tables or [None] * len(case.expected_value_columns), case.expected_value_columns):
        if table and not WAREHOUSE_SCHEMA.has_column(table, column):
            raise BenchmarkValidationError(f"line {line_no}: unknown column {table}.{column}")
    for dimension, value in case.expected_filters.items():
        dim = get_dimension(dimension)
        if not dim:
            raise BenchmarkValidationError(f"line {line_no}: unknown filter dimension {dimension}")
        if value not in dim.allowed_values:
            raise BenchmarkValidationError(f"line {line_no}: invalid filter value {dimension}={value}")
    for dimension in case.expected_dimensions:
        if not get_dimension(dimension):
            raise BenchmarkValidationError(f"line {line_no}: unknown dimension {dimension}")
    for period in case.expected_periods:
        if period not in QUARTERS:
            raise BenchmarkValidationError(f"line {line_no}: invalid period {period}")
    if case.expected_behavior == "execute" and not case.expected_metrics:
        raise BenchmarkValidationError(f"line {line_no}: executable case missing expected metrics")
    unsafe_terms = {"drop", "delete", "update", "insert", "alter", "create"}
    if case.expected_behavior == "execute" and any(term in case.question.lower() for term in unsafe_terms):
        raise BenchmarkValidationError(f"line {line_no}: executable case contains unsafe mutation wording")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=str(DEFAULT_PATH))
    args = parser.parse_args()
    cases = load_cases(Path(args.path))
    print(f"Valid SQL benchmark: {args.path} ({len(cases)} cases)")


if __name__ == "__main__":
    main()
