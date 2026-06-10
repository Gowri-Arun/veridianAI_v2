# Retrieval Evaluation

## Why Retrieval Evaluation Matters

Retrieval is the foundation of Veridian AI's grounded answer system. If the retriever does not surface the correct documents, no subsequent step (SQL reasoning, answer synthesis, verification) can compensate. Measuring retrieval quality independently ensures we can isolate retrieval failures from downstream failures.

## Benchmark Design

The retrieval gold benchmark (`benchmarks/retrieval_gold.jsonl`) contains curated queries where the expected set of documents is known. Each query is annotated with:

- **id** — unique identifier
- **query** — natural language question
- **query_type** — type from Veridian AI's intent taxonomy
- **difficulty** — easy, medium, or hard
- **expected_docs** — ground-truth document IDs that should be retrieved
- **expected_metrics** — metrics referenced by the query
- **expected_filters** — filters implied by the query
- **known_traps** — common mistakes the system should avoid
- **notes** — additional context

### Source

Queries are derived from `benchmarks/enterpriseqa_v0.jsonl` and extended with additional retrieval-focused variants. Every `expected_doc` matches a real `doc_id` in `data/processed/document_chunks.jsonl` (20 documents, 120 chunks).

## Gold Expected Documents

Each gold query includes one or more expected document IDs. The expectation is that the retriever should surface these documents in its top results. For example:

- Query *"What does churn rate mean?"* expects `["kpi_definitions"]`
- Query *"Why did APAC Enterprise revenue decline while marketing spend increased?"* expects `["q4_apac_revenue_report", "pricing_change_memo", "support_escalation_report", "marketing_campaign_memo"]`

## Metrics

### Recall@K

Fraction of expected documents found in the top K retrieved results.

```
Recall@K = |expected_docs ∩ retrieved_docs[:K]| / |expected_docs|
```

- Range: [0.0, 1.0]
- Higher is better
- Empty expected list returns 0.0

### Hit@K

Binary indicator: 1 if at least one expected document appears in the top K results, else 0.

```
Hit@K = 1 if expected_docs ∩ retrieved_docs[:K] ≠ ∅ else 0
```

- Range: [0.0, 1.0]
- Higher is better

### MRR (Mean Reciprocal Rank)

The average of reciprocal ranks across queries. Reciprocal rank is `1/rank` of the first relevant document (0 if none found).

```
ReciprocalRank = 1 / rank_of_first_relevant_doc
MRR = mean(reciprocal_ranks)
```

- Range: [0.0, 1.0]
- Higher is better

## BM25 Baseline Results

| Metric | Value |
|--------|-------|
| Benchmark Size | 25 queries |
| Average Recall@3 | 0.6500 |
| Average Recall@5 | 0.7833 |
| Average Recall@10 | 0.8533 |
| Hit Rate@3 | 0.8800 |
| Hit Rate@5 | 0.9200 |
| Hit Rate@10 | 0.9200 |
| MRR | 0.6500 |
| Failed Cases | 7 (28%) |

BM25 retrieves at least one relevant document for 92% of queries (Hit@10), but average Recall@10 is 0.85, indicating that some expected documents are missed. The MRR of 0.65 suggests relevant documents tend to appear at rank 1-2 on average.

## Failure Categories

| Label | Meaning |
|-------|---------|
| `no_failure` | At least one expected doc appears in top results |
| `missing_expected_doc` | No expected document retrieved at all |
| `generic_doc_ranked_too_high` | Expected doc found but ranked at position >= 5 |
| `weak_query_terms` | Query terms do not overlap with expected document content |
| `metadata_mismatch` | Document metadata does not align with query filters |
| `business_synonym_gap` | Business terminology differs from document language |
| `metric_confusion` | Query involves metric comparisons that confuse BM25 |

## Current Limitations

- BM25 is purely lexical; semantic matches are missed
- No query expansion or synonym-aware retrieval
- Small corpus (20 documents, 120 chunks)
- Gold labels are synthetic

## Next Step: Vector Retrieval

Implement embedding-based retrieval using sentence transformers. Compare Recall@K and MRR against the BM25 baseline. If vector retrieval shows meaningful improvement, build a hybrid retriever combining both approaches with weighted scoring.
