# Week 4 Review — BM25 Retrieval Evaluation Benchmark

## What Was Implemented

Week 4 delivered the first retrieval evaluation benchmark for Veridian AI's BM25 retriever. The existing BM25 retriever is now measured against a gold-standard benchmark using standard information retrieval metrics.

### Files Created

| File | Purpose |
|------|---------|
| `benchmarks/retrieval_gold.jsonl` | 25 retrieval gold queries with expected document IDs |
| `app/evaluation/retrieval_metrics.py` | Recall@K, Hit@K, Reciprocal Rank, MRR, Expected Doc Coverage |
| `app/evaluation/retrieval_eval.py` | Evaluation runner with per-query scoring, aggregate summary, failure classification |
| `scripts/run_retrieval_eval.py` | Script to run evaluation, save JSON/CSV, generate Markdown report |
| `tests/unit/test_retrieval_metrics.py` | 22 unit tests for metric functions |
| `tests/integration/test_retrieval_eval.py` | 12 integration tests for the evaluator |
| `docs/retrieval_evaluation.md` | Documentation of evaluation methodology |
| `docs/week4_review.md` | This file |

### Files Modified

| File | Change |
|------|--------|
| `README.md` | Updated status and roadmap with BM25 evaluation results |

### Benchmark Size

25 retrieval gold queries covering easy, medium, and hard difficulty across multiple query types.

### Metrics Implemented

- Recall@3, Recall@5, Recall@10
- Hit@3, Hit@5, Hit@10
- Reciprocal Rank (per-query)
- Mean Reciprocal Rank (aggregate)
- Expected Doc Coverage

### Failure Classification

7 failure labels: `no_failure`, `missing_expected_doc`, `generic_doc_ranked_too_high`, `weak_query_terms`, `metadata_mismatch`, `business_synonym_gap`, `metric_confusion`.

### BM25 Baseline Results

| Metric | Value |
|--------|-------|
| Average Recall@3 | 0.6500 |
| Average Recall@5 | 0.7833 |
| Average Recall@10 | 0.8533 |
| Hit Rate@3 | 0.8800 |
| Hit Rate@5 | 0.9200 |
| Hit Rate@10 | 0.9200 |
| MRR | 0.6500 |

### Failed Retrieval Cases

7 queries had retrieval failures:

| ID | Query | Failure | Expected | Recall@10 |
|----|-------|---------|----------|-----------|
| rg_009 | Which regions missed revenue or margin targets in Q4 2025? | weak_query_terms | regional_taxonomy, q4_business_review | 0.0000 |
| rg_020 | Summarize the Q4 2025 business review across all regions. | missing_expected_doc | q4_business_review | 0.0000 |
| rg_005 | What evidence suggests pricing changes affected APAC Enterprise? | generic_doc_ranked_too_high | pricing_change_memo, q4_apac_revenue_report | 1.0000 |
| rg_007 | What was the FlowOps v2.0 Q4 release side effect for Enterprise? | generic_doc_ranked_too_high | flowops_release_incident, product_release_notes, enterprise_retention_notes, q4_business_review | 1.0000 |
| rg_011 | What drove the SMB churn spike after support slowed down? | generic_doc_ranked_too_high | smb_churn_review, customer_success_notes, support_escalation_report, q4_business_review | 0.7500 |
| rg_012 | Why did APAC Enterprise revenue decline while marketing spend increased? | generic_doc_ranked_too_high | q4_apac_revenue_report, pricing_change_memo, support_escalation_report, marketing_campaign_memo | 1.0000 |
| rg_023 | What were the Q1, Q2, Q3, and Q4 2025 business reviews? | generic_doc_ranked_too_high | q1_business_review, q2_business_review, q3_business_review, q4_business_review | 0.5000 |

## What Improved from Week 3

- BM25 retriever now has a quantitative benchmark
- Retrieval metrics are implemented and tested
- Evaluation can be re-run to track progress
- Failure cases are classified for targeted improvement

## Known Limitations

- BM25 is purely lexical — no semantic understanding
- No query expansion or synonym-aware retrieval
- Only 20 documents (120 chunks) in the corpus
- Gold labels are synthetic

## Week 5 Goal

Implement vector retrieval (embedding-based) and compare against the BM25 baseline. If vector retrieval improves results, implement hybrid retrieval combining BM25 and vector scores, then evaluate reranking.
