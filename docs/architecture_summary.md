# Architecture Summary

## Overview

Veridian AI is organized as a modular pipeline where each stage of question answering is separated into its own component with defined interfaces, tests, and evaluation metrics. This separation enables independent development, debugging, and benchmarking.

## High-Level Data Flow

```
User Question
    │
    ▼
┌─────────────────────┐
│  Query Understanding │  Intent classification, term disambiguation
│  / Planning          │  Decide evidence sources needed (docs, SQL, both)
└─────────┬───────────┘
          │ plan
          ▼
┌─────────────────────┐
│  Document Retrieval  │  Hybrid search: BM25 + dense embeddings + re-ranking
│  (app/retrieval/)    │  Query rewriting, citation extraction
└─────────┬───────────┘
          │ relevant chunks
          ▼
┌─────────────────────┐
│  SQL / Structured   │  Schema-aware SQL generation + validation + execution
│  Data Reasoning     │  DuckDB analytics engine
│  (app/sql_engine/)  │
└─────────┬───────────┘
          │ SQL results
          ▼
┌─────────────────────┐
│  Evidence Collection │  Combine retrieved documents + SQL results
│  / Analysis          │  Metric comparison, trend identification
└─────────┬───────────┘
          │ evidence
          ▼
┌─────────────────────┐
│  Answer Generation   │  Structured synthesis with citations
│  (app/agents/)       │
└─────────┬───────────┘
          │ draft answer
          ▼
┌─────────────────────┐
│  Verification        │  Citation checking, claim verification,
│  (app/verification/) │  contradiction detection, confidence calibration
└─────────┬───────────┘
          │ verified answer
          ▼
┌─────────────────────┐
│  Evaluation Report   │  Compute metrics against benchmark gold answers
│  (app/evaluation/)   │  Trace logging, latency/cost tracking
└─────────────────────┘
```

## Backend (`app/`)

The backend uses FastAPI and is organized into these sub-packages:

| Package | Responsibility |
| --- | --- |
| `app/api/` | REST endpoints for query, evaluation, and health |
| `app/agents/` | Agent implementations for intent, planning, retrieval, SQL, synthesis, verification |
| `app/analysis/` | Data analysis utilities (trends, segments, anomalies) |
| `app/core/` | Configuration, constants, logging, security |
| `app/evaluation/` | Benchmark loading, metric computation, report generation |
| `app/ingestion/` | Document loading, chunking, metadata extraction |
| `app/llm/` | LLM client, prompt templates, token counting |
| `app/retrieval/` | BM25, dense, and hybrid retrieval; re-ranking; citation building |
| `app/schemas/` | Pydantic models for query, intent, plan, retrieval, SQL, verification |
| `app/semantic_layer/` | Business term resolution, metric/dimension registry, synonym mapping |
| `app/sql_engine/` | SQL generation, validation, execution, schema context |
| `app/utils/` | Shared utilities (JSON, text, IDs, dataframes) |
| `app/verification/` | Citation, claim, contradiction, and SQL result checking |
| `app/workflow/` | LangGraph orchestration, graph state, trace recording |

## Frontend (`frontend/`)

The frontend is a Streamlit application with multiple pages:

- **Query Engine** — main interface for asking questions and viewing answers
- **Execution Trace** — detailed view of pipeline steps
- **Evaluation Dashboard** — benchmark metrics and results
- **Failure Analysis** — categorization and analysis of failure modes
- **Ablation Results** — comparison of different system configurations

## Ingestion Pipeline

The ingestion pipeline (`app/ingestion/`) processes raw data into searchable artifacts:

```
Raw unstructured docs (Markdown with YAML frontmatter)
    → Document loader
    → Chunker (overlapping chunks)
    → Metadata extractor
    → document_chunks.jsonl + document_metadata.jsonl

Raw structured tables (CSV)
    → Table loader (pandas)
    → DuckDB warehouse (veridian.duckdb)
    → Schema snapshot + table profiles
```

## Benchmark Data

The `benchmarks/` directory contains:

- **enterpriseqa_v0.jsonl** — primary benchmark with 11 query types
- **adversarial_queries.jsonl** — inputs designed to test robustness
- **ambiguous_queries.jsonl** — questions requiring disambiguation
- **sql_gold.jsonl** — reference SQL queries
- **retrieval_gold.jsonl** — expected document results
- **answer_gold.jsonl** — reference answers
- **unanswerable_queries.jsonl** — questions the system should refuse

## Retrieval / Planning / Verification Direction

Each of these modules follows a consistent approach:

- **Retrieval** — supports BM25 (via `rank_bm25`), dense embeddings (via `sentence-transformers`), FAISS indexing, hybrid fusion, and cross-encoder re-ranking. The retrieval pipeline also includes query rewriting for improved recall.

- **Planning** — the planner agent determines the execution path: document-only, SQL-only, hybrid, or clarification. Planning is guided by the semantic layer and intent classification.

- **Verification** — applies deterministic checks after generation: citation verification (do cited sources support the claim?), claim extraction and grounding, contradiction detection between SQL results and synthesized text, numeric claim verification, confidence calibration, and optional answer revision.

## Evaluation-Driven Design

Every component is paired with evaluation metrics:

- Retrieval: Recall@K, MRR, precision
- SQL: execution accuracy, schema coverage
- Faithfulness: claim-level grounding rate
- Hallucination: unsupported claim detection
- Latency: end-to-end and per-component timing
- Cost: token usage tracking
- Ablation: configurable experiments to measure component impact
