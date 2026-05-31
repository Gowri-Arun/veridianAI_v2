# Week 2 Review: Synthetic Enterprise Dataset + Ingestion Pipeline

## 1. Week 2 Goal

Week 2 finalized the Veridian AI synthetic enterprise data foundation. The goal was to create a benchmarkable dataset with structured business metrics, internal document evidence, processed ingestion artifacts, and a DuckDB warehouse that can support Week 3 retrieval work.

## 2. What Was Created

- 9 structured CSV files in `data/raw/structured/`
- 20 markdown documents in `data/raw/unstructured/`
- Processed document chunks and metadata in `data/processed/`
- Table profiles for every structured table
- A schema snapshot for document and metric coverage
- A DuckDB warehouse at `data/warehouse/veridian.duckdb`
- An aligned enterprise benchmark at `benchmarks/enterpriseqa_v0.jsonl`

## 3. Structured Data Summary

The structured dataset covers revenue, customers, marketing spend, churn, support tickets, product usage, sales pipeline, subscriptions, and regional targets.

Current row counts:

- `revenue.csv`: 144 rows
- `customers.csv`: 400 rows
- `marketing_spend.csv`: 48 rows
- `churn.csv`: 48 rows
- `support_tickets.csv`: 447 rows
- `product_usage.csv`: 144 rows
- `sales_pipeline.csv`: 48 rows
- `subscriptions.csv`: 496 rows
- `region_targets.csv`: 16 rows

## 4. Unstructured Document Summary

The unstructured corpus contains 20 internal markdown documents. They include KPI definitions, schema definitions, regional taxonomy, quarterly reviews, pricing and marketing memos, support escalation analysis, release notes, customer success notes, segment guidance, and known metric confusion notes.

## 5. Hidden Business Narratives

The dataset embeds several evidence-backed narratives:

- APAC Enterprise recognized revenue declines in Q4 despite increased marketing spend.
- EMEA pipeline expands, but recognized revenue lags because conversion falls and sales cycles lengthen.
- SMB churn rises after support response and resolution times slow down.
- FlowOps v2.0 creates Enterprise usage disruption and support escalation pressure.
- Revenue, bookings, and pipeline value are intentionally easy to confuse.
- Support escalation evidence is correlated with churn pressure but does not prove direct causation by itself.
- Product usage decline acts as a warning signal before churn.
- Regional target performance can be checked against actual structured metrics.
- Gross margin trends are available in the revenue table.

## 6. Ingestion Pipeline Summary

The ingestion pipeline loads markdown documents, extracts and normalizes frontmatter metadata, chunks documents with section-aware logic, and writes JSONL outputs. It also profiles structured tables and builds the DuckDB warehouse.

The chunking pipeline is section-aware and preserves document identity, title, document type, metadata, chunk index, text, and source path for each chunk.

## 7. Processed Artifacts

Current processed artifacts:

- `document_chunks.jsonl`: 90 document chunks
- `document_metadata.jsonl`: 20 document metadata records
- `table_profiles.json`: profiles for 9 structured tables
- `schema_snapshot.json`: document counts, chunk counts, document type counts, quarter coverage, region coverage, segment coverage, related metrics, source files, and generation timestamp

## 8. DuckDB Warehouse

The warehouse file is `data/warehouse/veridian.duckdb`.

Expected tables:

- `revenue`
- `customers`
- `marketing_spend`
- `churn`
- `support_tickets`
- `product_usage`
- `sales_pipeline`
- `subscriptions`
- `region_targets`

The Week 2 validation gate confirms table presence, key row counts, revenue aggregation, and the APAC Enterprise Q4 revenue decline narrative.

## 9. Benchmark Alignment

`benchmarks/enterpriseqa_v0.jsonl` is aligned to real Week 2 files, table names, and documented metrics. It covers simple document questions, SQL lookups, hybrid evidence questions, ambiguity handling, contradiction handling, and unanswerable cases.

The benchmark emphasizes the main business narratives while avoiding retrieval implementation details.

## 10. Tests and Validation

Week 2 validation includes:

- Required raw CSV existence checks
- Required markdown document existence checks
- Loader checks through `load_tables` and `load_documents`
- JSONL validity checks with no empty lines
- Chunk uniqueness and metadata checks
- Source path preservation checks
- Table profile schema checks
- Schema snapshot taxonomy checks
- DuckDB table and narrative checks
- Benchmark alignment checks
- Banned keyword checks

## 11. Known Limitations

- Synthetic data patterns are intentionally visible for benchmarkability.
- No retrieval has been implemented yet.
- No embeddings have been implemented yet.
- No BM25 has been implemented yet.
- No LLM calls are part of Week 2.
- Chunking is section-aware but not semantically optimized yet.
- Causation is simulated through evidence, not statistically proven.

## 12. Week 3 Goal

Week 3 will build the first retrieval layer over the processed document chunks, starting with BM25 and retrieval evaluation.
