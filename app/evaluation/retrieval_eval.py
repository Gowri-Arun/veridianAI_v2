import json
import os
from pathlib import Path

from app.evaluation.retrieval_metrics import (
    hit_at_k,
    mean_reciprocal_rank,
    recall_at_k,
    reciprocal_rank,
)
from app.retrieval.retrieval_pipeline import RetrievalPipeline


GOLD_PATH = Path("benchmarks/retrieval_gold.jsonl")
RETRIEVAL_TOP_K = 10

FAILURE_NO_FAILURE = "no_failure"
FAILURE_MISSING_EXPECTED = "missing_expected_doc"
FAILURE_GENERIC_HIGH = "generic_doc_ranked_too_high"
FAILURE_WEAK_TERMS = "weak_query_terms"
FAILURE_METADATA_MISMATCH = "metadata_mismatch"
FAILURE_SYNONYM_GAP = "business_synonym_gap"
FAILURE_METRIC_CONFUSION = "metric_confusion"


def load_gold(path: Path) -> list[dict]:
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def deduplicate_ordered(doc_ids: list[str]) -> list[str]:
    seen = set()
    result = []
    for doc_id in doc_ids:
        if doc_id not in seen:
            seen.add(doc_id)
            result.append(doc_id)
    return result


def assign_failure(
    retrieved_doc_ids: list[str],
    expected_doc_ids: list[str],
    query: str,
) -> str:
    if not expected_doc_ids:
        return FAILURE_NO_FAILURE
    retrieved_set = set(retrieved_doc_ids)
    expected_set = set(expected_doc_ids)
    found = expected_set & retrieved_set
    if found:
        for exp_doc in expected_doc_ids:
            if exp_doc in retrieved_set:
                rank = retrieved_doc_ids.index(exp_doc) + 1
                if rank >= 5:
                    return FAILURE_GENERIC_HIGH
        return FAILURE_NO_FAILURE
    query_lower = query.lower()
    if "confusion" in query_lower or "difference" in query_lower:
        if "kpi_definitions" in expected_doc_ids or "known_metric_confusions" in expected_doc_ids:
            return FAILURE_METRIC_CONFUSION
    for exp_doc in expected_doc_ids:
        doc_terms = exp_doc.replace("_", " ").lower().split()
        meaningful_doc_terms = [t for t in doc_terms if len(t) > 3]
        if meaningful_doc_terms:
            if any(t not in query_lower for t in meaningful_doc_terms):
                return FAILURE_WEAK_TERMS
    return FAILURE_MISSING_EXPECTED


def evaluate_single(
    pipeline: RetrievalPipeline,
    item: dict,
) -> dict:
    query = item["query"]
    expected_docs = item.get("expected_docs", [])
    results = pipeline.retrieve(query, top_k=RETRIEVAL_TOP_K)
    retrieved_doc_ids = [r.doc_id for r in results]
    retrieved_doc_ids = deduplicate_ordered(retrieved_doc_ids)
    r3 = recall_at_k(retrieved_doc_ids, expected_docs, 3)
    r5 = recall_at_k(retrieved_doc_ids, expected_docs, 5)
    r10 = recall_at_k(retrieved_doc_ids, expected_docs, 10)
    h3 = hit_at_k(retrieved_doc_ids, expected_docs, 3)
    h5 = hit_at_k(retrieved_doc_ids, expected_docs, 5)
    h10 = hit_at_k(retrieved_doc_ids, expected_docs, 10)
    rr = reciprocal_rank(retrieved_doc_ids, expected_docs)
    failure = assign_failure(retrieved_doc_ids, expected_docs, query)
    return {
        "id": item["id"],
        "query": query,
        "query_type": item.get("query_type", ""),
        "difficulty": item.get("difficulty", ""),
        "expected_docs": expected_docs,
        "retrieved_docs": retrieved_doc_ids,
        "recall_at_3": round(r3, 4),
        "recall_at_5": round(r5, 4),
        "recall_at_10": round(r10, 4),
        "hit_at_3": round(h3, 4),
        "hit_at_5": round(h5, 4),
        "hit_at_10": round(h10, 4),
        "reciprocal_rank": round(rr, 4),
        "failure_reason": failure,
    }


def compute_summary(per_query: list[dict]) -> dict:
    n = len(per_query)
    if n == 0:
        return {
            "num_queries": 0,
            "average_recall_at_3": 0.0,
            "average_recall_at_5": 0.0,
            "average_recall_at_10": 0.0,
            "hit_rate_at_3": 0.0,
            "hit_rate_at_5": 0.0,
            "hit_rate_at_10": 0.0,
            "mrr": 0.0,
        }
    avg_r3 = sum(r["recall_at_3"] for r in per_query) / n
    avg_r5 = sum(r["recall_at_5"] for r in per_query) / n
    avg_r10 = sum(r["recall_at_10"] for r in per_query) / n
    hr3 = sum(r["hit_at_3"] for r in per_query) / n
    hr5 = sum(r["hit_at_5"] for r in per_query) / n
    hr10 = sum(r["hit_at_10"] for r in per_query) / n
    mrr = mean_reciprocal_rank([r["reciprocal_rank"] for r in per_query])
    return {
        "num_queries": n,
        "average_recall_at_3": round(avg_r3, 4),
        "average_recall_at_5": round(avg_r5, 4),
        "average_recall_at_10": round(avg_r10, 4),
        "hit_rate_at_3": round(hr3, 4),
        "hit_rate_at_5": round(hr5, 4),
        "hit_rate_at_10": round(hr10, 4),
        "mrr": round(mrr, 4),
    }


def run_evaluation(
    gold_path: Path = GOLD_PATH,
) -> tuple[list[dict], dict]:
    if not os.environ.get("VERIDIAN_EVAL_QUIET"):
        pass
    gold = load_gold(gold_path)
    pipeline = RetrievalPipeline()
    per_query = []
    for item in gold:
        result = evaluate_single(pipeline, item)
        per_query.append(result)
    summary = compute_summary(per_query)
    return per_query, summary
