from app.schemas.benchmark import BenchmarkCaseResult, SQLBenchmarkSummary


METRIC_NAMES = [
    "semantic_parse_accuracy",
    "metric_selection_accuracy",
    "dimension_selection_accuracy",
    "filter_accuracy",
    "period_accuracy",
    "query_shape_accuracy",
    "table_selection_accuracy",
    "column_selection_accuracy",
    "aggregation_accuracy",
    "grouping_accuracy",
    "execution_success_rate",
    "result_accuracy",
    "comparison_accuracy",
    "clarification_accuracy",
    "unsupported_rejection_accuracy",
    "adversarial_block_rate",
    "overall_case_accuracy",
]


def _rate(passed: int, total: int) -> float:
    return round(passed / total, 4) if total else 0.0


def summarize_results(results: list[BenchmarkCaseResult]) -> SQLBenchmarkSummary:
    total = len(results)
    passed = sum(1 for r in results if r.status == "passed")
    counts = {"total": total, "passed": passed, "failed": total - passed}
    metrics: dict[str, float] = {}
    for name in METRIC_NAMES:
        applicable = [r for r in results if name in r.checks]
        metrics[name] = _rate(sum(1 for r in applicable if r.checks[name]), len(applicable))
        counts[f"{name}_total"] = len(applicable)
        counts[f"{name}_passed"] = sum(1 for r in applicable if r.checks[name])
    failure_counts: dict[str, int] = {}
    for result in results:
        for failure in result.failures:
            failure_counts[failure.failure_category] = failure_counts.get(failure.failure_category, 0) + 1
    return SQLBenchmarkSummary(
        total_cases=total,
        passed_cases=passed,
        failed_cases=total - passed,
        metrics=metrics,
        counts=counts,
        failure_category_counts=failure_counts,
    )
