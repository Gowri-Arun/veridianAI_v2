from typing import Any, Literal

from pydantic import BaseModel, Field


ExpectedBehavior = Literal["execute", "reject", "requires_clarification", "unsupported"]
BenchmarkCategory = Literal[
    "metric_lookup",
    "grouped_metric",
    "period_comparison",
    "absolute_change",
    "percentage_change",
    "multiple_metrics",
    "top_n",
    "count_query",
    "ambiguous",
    "unsupported",
    "adversarial",
]
Difficulty = Literal["easy", "medium", "hard", "adversarial"]
CaseStatus = Literal["passed", "failed", "error"]
FailureCategory = Literal[
    "INTENT_MISCLASSIFICATION",
    "METRIC_RESOLUTION_ERROR",
    "DIMENSION_RESOLUTION_ERROR",
    "FILTER_EXTRACTION_ERROR",
    "TIME_NORMALIZATION_ERROR",
    "AMBIGUITY_HANDLING_ERROR",
    "VALIDATION_ERROR",
    "QUERY_SHAPE_ERROR",
    "TABLE_SELECTION_ERROR",
    "COLUMN_SELECTION_ERROR",
    "AGGREGATION_ERROR",
    "GROUPING_ERROR",
    "ORDERING_ERROR",
    "LIMIT_ERROR",
    "PARAMETERIZATION_ERROR",
    "SQL_SAFETY_ERROR",
    "EXECUTION_ERROR",
    "EMPTY_RESULT_ERROR",
    "NUMERIC_RESULT_ERROR",
    "COMPARISON_CALCULATION_ERROR",
    "EXPECTED_REJECTION_FAILED",
    "EXPECTED_CLARIFICATION_FAILED",
    "UNSUPPORTED_QUERY_EXECUTED",
    "UNEXPECTED_INTERNAL_ERROR",
]


class ExpectedResultSpec(BaseModel):
    columns: list[str] = Field(default_factory=list)
    row_count: int | None = None
    comparison_direction: str | None = None
    rows: list[dict[str, Any]] = Field(default_factory=list)


class SQLBenchmarkCase(BaseModel):
    id: str
    question: str
    category: BenchmarkCategory
    expected_behavior: ExpectedBehavior
    expected_query_shape: str | None = None
    expected_metrics: list[str] = Field(default_factory=list)
    expected_tables: list[str] = Field(default_factory=list)
    expected_value_columns: list[str] = Field(default_factory=list)
    expected_dimensions: list[str] = Field(default_factory=list)
    expected_filters: dict[str, Any] = Field(default_factory=dict)
    expected_periods: list[str] = Field(default_factory=list)
    expected_aggregation: str | None = None
    expected_order_by: list[str] = Field(default_factory=list)
    expected_limit: int | None = None
    expected_result: ExpectedResultSpec = Field(default_factory=ExpectedResultSpec)
    expected_error_codes: list[str] = Field(default_factory=list)
    expected_requires_clarification: bool = False
    must_execute_sql: bool = False
    known_traps: list[str] = Field(default_factory=list)
    difficulty: Difficulty


class BenchmarkFailure(BaseModel):
    case_id: str
    failure_category: FailureCategory
    stage: str
    message: str
    expected: Any = None
    actual: Any = None


class BenchmarkCaseResult(BaseModel):
    case_id: str
    category: BenchmarkCategory
    difficulty: Difficulty
    status: CaseStatus
    checks: dict[str, bool] = Field(default_factory=dict)
    failures: list[BenchmarkFailure] = Field(default_factory=list)
    executed_sql_count: int = 0
    row_count: int = 0


class SQLBenchmarkSummary(BaseModel):
    total_cases: int
    passed_cases: int
    failed_cases: int
    metrics: dict[str, float] = Field(default_factory=dict)
    counts: dict[str, int] = Field(default_factory=dict)
    failure_category_counts: dict[str, int] = Field(default_factory=dict)
