import os

import pytest

from app.evaluation.retrieval_eval import (
    FAILURE_NO_FAILURE,
    GOLD_PATH,
    assign_failure,
    compute_summary,
    deduplicate_ordered,
    evaluate_single,
    load_gold,
    run_evaluation,
)
from app.retrieval.retrieval_pipeline import RetrievalPipeline


class TestGoldBenchmark:
    def test_gold_jsonl_exists(self):
        assert GOLD_PATH.exists(), f"Gold benchmark not found: {GOLD_PATH}"

    def test_gold_jsonl_loads(self):
        items = load_gold(GOLD_PATH)
        assert len(items) >= 20, f"Expected at least 20 items, got {len(items)}"

    def test_each_item_has_required_fields(self):
        items = load_gold(GOLD_PATH)
        required = {"id", "query", "expected_docs"}
        for item in items:
            missing = required - set(item.keys())
            assert not missing, f"Item {item.get('id')} missing fields: {missing}"

    def test_expected_docs_are_strings(self):
        items = load_gold(GOLD_PATH)
        for item in items:
            for doc in item["expected_docs"]:
                assert isinstance(doc, str), f"Item {item['id']} has non-string doc: {doc}"


class TestDeduplicateOrdered:
    def test_no_duplicates(self):
        assert deduplicate_ordered(["a", "b", "c"]) == ["a", "b", "c"]

    def test_with_duplicates(self):
        assert deduplicate_ordered(["a", "b", "a", "c", "b"]) == ["a", "b", "c"]

    def test_empty(self):
        assert deduplicate_ordered([]) == []


class TestEvaluateSingle:
    @pytest.fixture
    def pipeline(self):
        return RetrievalPipeline()

    def test_result_contains_expected_fields(self, pipeline):
        item = {
            "id": "test_001",
            "query": "What does churn rate mean?",
            "query_type": "simple_document",
            "difficulty": "easy",
            "expected_docs": ["kpi_definitions"],
        }
        result = evaluate_single(pipeline, item)
        expected_fields = {
            "id", "query", "query_type", "difficulty",
            "expected_docs", "retrieved_docs",
            "recall_at_3", "recall_at_5", "recall_at_10",
            "hit_at_3", "hit_at_5", "hit_at_10",
            "reciprocal_rank", "failure_reason",
        }
        assert expected_fields.issubset(result.keys()), f"Missing fields: {expected_fields - result.keys()}"

    def test_metrics_between_zero_and_one(self, pipeline):
        item = {
            "id": "test_002",
            "query": "Define recognized revenue.",
            "query_type": "simple_document",
            "difficulty": "easy",
            "expected_docs": ["kpi_definitions"],
        }
        result = evaluate_single(pipeline, item)
        for key in ["recall_at_3", "recall_at_5", "recall_at_10", "hit_at_3", "hit_at_5", "hit_at_10", "reciprocal_rank"]:
            assert 0.0 <= result[key] <= 1.0, f"{key} out of bounds: {result[key]}"

    def test_failure_field_exists(self, pipeline):
        item = {
            "id": "test_003",
            "query": "What happened in Q4?",
            "query_type": "hybrid_sql_document",
            "difficulty": "medium",
            "expected_docs": ["q4_business_review"],
        }
        result = evaluate_single(pipeline, item)
        assert result["failure_reason"] is not None


class TestAssignFailure:
    def test_no_failure_when_expected_found(self):
        reason = assign_failure(["d1", "d2", "d3"], ["d1"], "test query")
        assert reason == FAILURE_NO_FAILURE

    def test_missing_expected_doc(self):
        reason = assign_failure(["d1", "d2"], ["d3"], "test query")
        assert reason == "missing_expected_doc"

    def test_empty_expected(self):
        reason = assign_failure(["d1", "d2"], [], "test query")
        assert reason == FAILURE_NO_FAILURE


class TestComputeSummary:
    def test_empty_input(self):
        summary = compute_summary([])
        assert summary["num_queries"] == 0
        assert summary["average_recall_at_3"] == 0.0

    def test_summary_contains_all_keys(self):
        per_query = [
            {
                "recall_at_3": 1.0, "recall_at_5": 1.0, "recall_at_10": 1.0,
                "hit_at_3": 1.0, "hit_at_5": 1.0, "hit_at_10": 1.0,
                "reciprocal_rank": 1.0,
            }
        ]
        summary = compute_summary(per_query)
        expected_keys = {
            "num_queries", "average_recall_at_3", "average_recall_at_5",
            "average_recall_at_10", "hit_rate_at_3", "hit_rate_at_5",
            "hit_rate_at_10", "mrr",
        }
        assert expected_keys.issubset(summary.keys())


class TestRunEvaluation:
    def test_evaluation_runs_on_small_subset(self):
        os.environ["VERIDIAN_EVAL_QUIET"] = "1"
        per_query, summary = run_evaluation()
        assert summary["num_queries"] >= 20
        assert len(per_query) == summary["num_queries"]

    def test_summary_has_non_negative_metrics(self):
        os.environ["VERIDIAN_EVAL_QUIET"] = "1"
        _, summary = run_evaluation()
        for key in ["average_recall_at_3", "average_recall_at_5", "average_recall_at_10",
                     "hit_rate_at_3", "hit_rate_at_5", "hit_rate_at_10", "mrr"]:
            assert 0.0 <= summary[key] <= 1.0, f"{key} out of bounds: {summary[key]}"

    def test_failed_cases_field_exists(self):
        os.environ["VERIDIAN_EVAL_QUIET"] = "1"
        per_query, _ = run_evaluation()
        failed = [r for r in per_query if r["failure_reason"] != FAILURE_NO_FAILURE]
        assert isinstance(failed, list)
