from app.schemas.semantic import SemanticParseResult
from app.schemas.sql import SQLFilter, SQLPlan, SQLPlanningError, SQLQuerySpec
from app.semantic_layer.dimension_registry import get_dimension
from app.semantic_layer.metric_registry import get_metric


class StructuredQueryPlanner:
    def plan(self, semantic: SemanticParseResult) -> SQLPlan:
        if semantic.errors or semantic.requires_clarification:
            return SQLPlan(
                errors=[
                    SQLPlanningError(
                        code="SEMANTIC_BLOCKED",
                        message="SQL planning skipped because semantic parsing produced errors or clarification requirements.",
                        details={"semantic_errors": [e.model_dump() for e in semantic.errors], "requires_clarification": semantic.requires_clarification},
                    )
                ]
            )
        if not semantic.metrics:
            return SQLPlan(errors=[SQLPlanningError(code="NO_METRIC", message="No supported metric was resolved for SQL planning.")])

        specs: list[SQLQuerySpec] = []
        errors: list[SQLPlanningError] = []
        for idx, metric_ref in enumerate(semantic.metrics):
            metric = get_metric(metric_ref.canonical_name)
            if not metric:
                errors.append(SQLPlanningError(code="UNKNOWN_METRIC", message=f"Unknown metric '{metric_ref.canonical_name}'."))
                continue
            query_shape = self._detect_shape(semantic, metric_ref.canonical_name)
            dimensions = [d.canonical_name for d in semantic.dimensions if d.canonical_name in metric.valid_dimensions]
            if query_shape == "top_n" and not dimensions:
                dimensions = ["region"]
            sql_filters: list[SQLFilter] = []
            for condition in semantic.filters:
                if condition.dimension == "quarter" and semantic.time_range and semantic.time_range.periods:
                    continue
                dim = get_dimension(condition.dimension)
                if not dim:
                    continue
                if condition.dimension in metric.valid_dimensions:
                    sql_filters.append(SQLFilter(column=dim.column_name, value=condition.value))
            periods = semantic.time_range.periods if semantic.time_range else []
            aggregation = metric_ref.aggregation if metric_ref.aggregation in metric.allowed_aggregations else metric.default_aggregation
            if query_shape == "count_query":
                aggregation = "count"
            specs.append(
                SQLQuerySpec(
                    query_id=f"sql_{idx + 1}",
                    query_shape=query_shape,
                    metric=metric.canonical_name,
                    source_table=metric.source_table,
                    value_column=metric.value_column,
                    aggregation=aggregation,
                    dimensions=dimensions,
                    filters=sql_filters,
                    periods=periods,
                    comparison=semantic.comparison.model_dump() if semantic.comparison else None,
                    order_by=metric.value_column if semantic.sort else None,
                    order_direction=semantic.sort.direction if semantic.sort else "desc",
                    limit=semantic.limit,
                )
            )
        return SQLPlan(specs=specs, errors=errors, warnings=[w.message for w in semantic.warnings])

    def _detect_shape(self, semantic: SemanticParseResult, metric_name: str):
        if semantic.sort:
            return "top_n"
        if semantic.comparison:
            if semantic.comparison.comparison_type == "absolute_change":
                return "absolute_change"
            if semantic.comparison.comparison_type == "percentage_change":
                return "percentage_change"
            return "period_comparison"
        if metric_name in {"customer_count", "support_tickets", "subscriptions"} and semantic.aggregation == "count":
            return "count_query"
        if semantic.dimensions:
            return "grouped_metric"
        return "metric_lookup"
