from typing import Any, Literal

from pydantic import BaseModel, Field


QueryShape = Literal[
    "metric_lookup",
    "grouped_metric",
    "period_comparison",
    "absolute_change",
    "percentage_change",
    "top_n",
    "count_query",
]


class SQLFilter(BaseModel):
    column: str
    value: Any


class SQLQuerySpec(BaseModel):
    query_id: str
    query_shape: QueryShape
    metric: str
    source_table: str
    value_column: str
    aggregation: str
    dimensions: list[str] = Field(default_factory=list)
    filters: list[SQLFilter] = Field(default_factory=list)
    periods: list[str] = Field(default_factory=list)
    comparison: dict[str, Any] | None = None
    order_by: str | None = None
    order_direction: Literal["asc", "desc"] = "desc"
    limit: int | None = None


class SQLPlanningError(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class SQLPlan(BaseModel):
    specs: list[SQLQuerySpec] = Field(default_factory=list)
    errors: list[SQLPlanningError] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class CompiledSQLQuery(BaseModel):
    query_id: str
    sql: str
    parameters: list[Any] = Field(default_factory=list)
    explanation: str


class SQLExecutionError(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class SQLExecutionResult(BaseModel):
    query_id: str
    columns: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0
    execution_ms: float | None = None
    warnings: list[str] = Field(default_factory=list)
    error: SQLExecutionError | None = None


class ComparisonResult(BaseModel):
    query_id: str
    baseline_period: str
    comparison_period: str
    baseline_value: float | None = None
    comparison_value: float | None = None
    absolute_change: float | None = None
    percentage_change: float | None = None
    direction: Literal["increase", "decrease", "flat", "unknown"] = "unknown"
    warnings: list[str] = Field(default_factory=list)
