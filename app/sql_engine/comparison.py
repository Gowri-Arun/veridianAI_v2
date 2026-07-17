from app.schemas.sql import ComparisonResult, SQLExecutionResult, SQLQuerySpec


def calculate_comparison(spec: SQLQuerySpec, result: SQLExecutionResult) -> ComparisonResult | None:
    if spec.query_shape not in {"absolute_change", "percentage_change"}:
        return None
    if not spec.periods or len(spec.periods) < 2:
        return None
    baseline_period = spec.periods[0]
    comparison_period = spec.periods[-1]
    values = {row.get("quarter"): row.get(spec.metric) for row in result.rows}
    baseline = values.get(baseline_period)
    comparison = values.get(comparison_period)
    warnings: list[str] = []
    absolute_change = None
    percentage_change = None
    direction = "unknown"
    if baseline is None or comparison is None:
        warnings.append("One or more comparison periods are missing from the SQL result.")
    else:
        baseline_float = float(baseline)
        comparison_float = float(comparison)
        absolute_change = round(comparison_float - baseline_float, 4)
        if absolute_change > 0:
            direction = "increase"
        elif absolute_change < 0:
            direction = "decrease"
        else:
            direction = "flat"
        if spec.query_shape == "percentage_change":
            if baseline_float == 0:
                warnings.append("Percentage change is undefined because the baseline value is zero.")
            else:
                percentage_change = round((absolute_change / baseline_float) * 100, 4)
    return ComparisonResult(
        query_id=spec.query_id,
        baseline_period=baseline_period,
        comparison_period=comparison_period,
        baseline_value=float(baseline) if baseline is not None else None,
        comparison_value=float(comparison) if comparison is not None else None,
        absolute_change=absolute_change,
        percentage_change=percentage_change,
        direction=direction,
        warnings=warnings,
    )
