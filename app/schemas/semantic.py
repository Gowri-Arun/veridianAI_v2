from typing import Any, Literal

from pydantic import BaseModel, Field


SemanticErrorCode = Literal[
    "UNKNOWN_METRIC",
    "AMBIGUOUS_METRIC",
    "UNKNOWN_DIMENSION",
    "UNKNOWN_FILTER_VALUE",
    "INVALID_DIMENSION_FOR_METRIC",
    "UNSUPPORTED_AGGREGATION",
    "MISSING_TIME_PERIOD",
    "INVALID_TIME_RANGE",
    "INVALID_COMPARISON",
    "UNSUPPORTED_QUERY_SHAPE",
]


class SemanticWarning(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class SemanticError(BaseModel):
    code: SemanticErrorCode
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class SemanticAmbiguity(BaseModel):
    source_term: str
    candidate_metrics: list[str] = Field(default_factory=list)
    reason: str
    requires_clarification: bool = True


class MetricReference(BaseModel):
    canonical_name: str
    display_name: str
    source_term: str
    source_table: str
    value_column: str
    aggregation: str


class DimensionReference(BaseModel):
    canonical_name: str
    display_name: str
    source_term: str
    column_name: str


class FilterCondition(BaseModel):
    dimension: str
    column_name: str
    value: Any
    source_term: str


class NormalizedTimeRange(BaseModel):
    grain: Literal["quarter", "year"] = "quarter"
    periods: list[str] = Field(default_factory=list)
    start_period: str | None = None
    end_period: str | None = None
    reference_period: str | None = None
    is_relative: bool = False
    warnings: list[str] = Field(default_factory=list)


class ComparisonSpec(BaseModel):
    comparison_type: Literal["period", "absolute_change", "percentage_change"] | None = None
    baseline_period: str | None = None
    comparison_period: str | None = None


class SortSpec(BaseModel):
    metric: str
    direction: Literal["asc", "desc"] = "desc"


class SemanticParseResult(BaseModel):
    original_query: str
    canonical_query: str
    mapped_terms: dict[str, str] = Field(default_factory=dict)
    metrics: list[MetricReference] = Field(default_factory=list)
    dimensions: list[DimensionReference] = Field(default_factory=list)
    filters: list[FilterCondition] = Field(default_factory=list)
    time_range: NormalizedTimeRange | None = None
    aggregation: str | None = None
    comparison: ComparisonSpec | None = None
    sort: SortSpec | None = None
    limit: int | None = None
    warnings: list[SemanticWarning] = Field(default_factory=list)
    errors: list[SemanticError] = Field(default_factory=list)
    ambiguities: list[SemanticAmbiguity] = Field(default_factory=list)
    requires_clarification: bool = False

    def to_compat_dict(self) -> dict[str, Any]:
        warnings: list[Any] = [w.message for w in self.warnings]
        metric_names = [m.canonical_name for m in self.metrics]
        if "pipeline" in metric_names and "sales_pipeline" not in metric_names:
            metric_names.append("sales_pipeline")
        return {
            "original_query": self.original_query,
            "canonical_query": self.canonical_query,
            "mapped_terms": self.mapped_terms,
            "metrics": metric_names,
            "dimensions": [d.canonical_name for d in self.dimensions],
            "filters": {f.dimension: f.value for f in self.filters},
            "time_range": self.time_range.model_dump() if self.time_range else None,
            "aggregation": self.aggregation,
            "comparison": self.comparison.model_dump() if self.comparison else None,
            "sort": self.sort.model_dump() if self.sort else None,
            "limit": self.limit,
            "warnings": warnings,
            "errors": [e.model_dump() for e in self.errors],
            "ambiguities": [a.model_dump() for a in self.ambiguities],
            "requires_clarification": self.requires_clarification,
            "typed": self.model_dump(),
        }
