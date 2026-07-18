from app.evaluation.sql_metrics import summarize_results
from app.schemas.benchmark import BenchmarkCaseResult


def test_empty_metrics_do_not_divide_by_zero():
    summary = summarize_results([])
    assert summary.total_cases == 0
    assert summary.metrics["overall_case_accuracy"] == 0.0


def test_metric_calculation():
    results = [
        BenchmarkCaseResult(case_id="a", category="metric_lookup", difficulty="easy", status="passed", checks={"overall_case_accuracy": True, "execution_success_rate": True}),
        BenchmarkCaseResult(case_id="b", category="metric_lookup", difficulty="easy", status="failed", checks={"overall_case_accuracy": False, "execution_success_rate": True}),
    ]
    summary = summarize_results(results)
    assert summary.metrics["overall_case_accuracy"] == 0.5
    assert summary.metrics["execution_success_rate"] == 1.0
