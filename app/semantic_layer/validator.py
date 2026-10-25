from app.schemas.semantic import SemanticError, SemanticParseResult
from app.semantic_layer.dimension_registry import get_dimension
from app.semantic_layer.metric_registry import get_metric


class SemanticValidator:
    def validate(self, result: SemanticParseResult) -> SemanticParseResult:
        errors = list(result.errors)

        for metric in result.metrics:
            metric_def = get_metric(metric.canonical_name)
            if not metric_def:
                errors.append(SemanticError(code="UNKNOWN_METRIC", message=f"Unknown metric '{metric.canonical_name}'."))
                continue
            if metric.aggregation not in metric_def.allowed_aggregations:
                errors.append(
                    SemanticError(
                        code="UNSUPPORTED_AGGREGATION",
                        message=f"Aggregation '{metric.aggregation}' is not supported for {metric.canonical_name}.",
                        details={"metric": metric.canonical_name, "allowed": metric_def.allowed_aggregations},
                    )
                )

        for dimension in result.dimensions:
            dim_def = get_dimension(dimension.canonical_name)
            if not dim_def:
                errors.append(SemanticError(code="UNKNOWN_DIMENSION", message=f"Unknown dimension '{dimension.canonical_name}'."))
                continue
            if result.metrics and not any(metric.canonical_name in dim_def.compatible_metrics for metric in result.metrics):
                errors.append(
                    SemanticError(
                        code="INVALID_DIMENSION_FOR_METRIC",
                        message=f"Dimension '{dimension.canonical_name}' is not valid for any requested metric.",
                        details={"dimension": dimension.canonical_name, "metrics": [m.canonical_name for m in result.metrics]},
                    )
                )

        for condition in result.filters:
            dim_def = get_dimension(condition.dimension)
            if not dim_def:
                errors.append(SemanticError(code="UNKNOWN_DIMENSION", message=f"Unknown filter dimension '{condition.dimension}'."))
                continue
            if condition.value not in dim_def.allowed_values:
                errors.append(
                    SemanticError(
                        code="UNKNOWN_FILTER_VALUE",
                        message=f"Unknown value '{condition.value}' for dimension '{condition.dimension}'.",
                        details={"dimension": condition.dimension, "allowed_values": dim_def.allowed_values},
                    )
                )
            if result.metrics and not any(metric.canonical_name in dim_def.compatible_metrics for metric in result.metrics):
                errors.append(
                    SemanticError(
                        code="INVALID_DIMENSION_FOR_METRIC",
                        message=f"Filter '{condition.dimension}' is not valid for any requested metric.",
                        details={"dimension": condition.dimension, "metrics": [m.canonical_name for m in result.metrics]},
                    )
                )

        if result.comparison and result.comparison.comparison_type in {"period", "absolute_change", "percentage_change"}:
            periods = result.time_range.periods if result.time_range else []
            if len(periods) < 2:
                errors.append(SemanticError(code="INVALID_COMPARISON", message="Comparison queries require at least two periods."))

        result.errors = errors
        result.requires_clarification = result.requires_clarification or bool(result.ambiguities)
        return result
