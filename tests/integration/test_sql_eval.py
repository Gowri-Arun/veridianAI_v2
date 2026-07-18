from app.evaluation.sql_eval import run_evaluation
from scripts.validate_sql_benchmark import DEFAULT_PATH, load_cases


def test_sql_gold_loads():
    cases = load_cases(DEFAULT_PATH)
    assert len(cases) >= 50


def test_metric_lookup_evaluates():
    results, summary = run_evaluation(case_id="sql_001")
    assert summary.total_cases == 1
    assert results[0].executed_sql_count == 1


def test_adversarial_blocked():
    results, _ = run_evaluation(case_id="sql_052")
    assert results[0].executed_sql_count == 0
    assert results[0].checks["adversarial_block_rate"] is True


def test_ambiguous_requires_clarification():
    results, _ = run_evaluation(case_id="sql_046")
    assert results[0].executed_sql_count == 0
    assert results[0].checks["clarification_accuracy"] is True


def test_small_end_to_end_subset():
    subset = ["sql_001", "sql_009", "sql_016", "sql_028", "sql_033", "sql_038", "sql_046", "sql_049", "sql_052", "sql_053"]
    for case_id in subset:
        results, _ = run_evaluation(case_id=case_id)
        assert results
