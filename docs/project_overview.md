# Project Overview: Veridian AI

## Problem

Enterprise teams need reliable answers from a mix of structured and unstructured data sources. A typical question such as "Why did enterprise revenue drop in APAC last quarter despite increased marketing spend?" requires:

- Understanding ambiguous business terminology
- Retrieving relevant unstructured documents (pricing memos, support reports, business reviews)
- Querying structured data (revenue tables, churn data, marketing spend)
- Combining evidence from both sources
- Synthesizing a grounded answer with citations
- Verifying that claims are supported by evidence

Current approaches that rely on prompting an LLM without grounding, verification, or systematic evaluation are not suitable for enterprise use.

## Motivation

The goal of Veridian AI is to explore how to make LLM-based enterprise analytics systems more reliable, measurable, and explainable. The project focuses on:

- **Evaluation-first design** — every component is developed with corresponding benchmarks and metrics
- **Deterministic fallbacks** — tasks that can be checked by code (SQL validation, citation checking, numeric claim verification) are not delegated to an LLM
- **Reproducibility** — synthetic data, defined benchmarks, and documented workflows enable repeatable experimentation
- **Modularity** — ingestion, retrieval, SQL reasoning, planning, verification, and evaluation are developed as separate modules

## System Design

The system follows a modular pipeline:

1. **Query Understanding** — classify question type and extract intent
2. **Planning** — determine what evidence sources are needed (documents, SQL, or both)
3. **Retrieval** — find relevant unstructured documents via hybrid search (BM25 + dense embeddings)
4. **SQL Reasoning** — generate, validate, and execute queries against a DuckDB warehouse
5. **Analysis** — compare metrics and identify patterns from retrieved data
6. **Synthesis** — combine evidence into a structured answer with citations
7. **Verification** — check citations, claims, contradictions, and numeric accuracy
8. **Evaluation** — log full traces and compute metrics against benchmark gold standards

## Key Modules

| Module | Purpose |
| --- | --- |
| `app/ingestion/` | Document loading, chunking, metadata extraction, table loading |
| `app/retrieval/` | BM25, dense, and hybrid retrieval; query rewriting; re-ranking |
| `app/sql_engine/` | SQL generation, validation, execution, schema management |
| `app/semantic_layer/` | Business term resolution, synonym mapping, metric registry |
| `app/agents/` | Intent analysis, planning, retrieval, SQL, synthesis, verification |
| `app/evaluation/` | Benchmark loading, retrieval/SQL/synthesis evaluation, report generation |
| `app/verification/` | Citation checking, claim extraction, contradiction detection |
| `app/workflow/` | LangGraph-based orchestration, trace recording, fallback logic |

## Current Status

**Status: In progress**

Completed:
- Repository structure and project documentation
- FastAPI backend with health and query endpoints
- Streamlit UI scaffold with query, trace, evaluation, failure analysis, and ablation pages
- Synthetic enterprise dataset (9 tables, 20+ document narratives, embedded business scenarios)
- Document ingestion pipeline (loading, chunking, metadata extraction)
- DuckDB warehouse build
- BM25, FAISS, and hybrid retrieval infrastructure
- SQL engine with schema context, validation, and execution
- Evaluation framework (retrieval, SQL, faithfulness, hallucination, latency, cost, ablation)
- Verification layer (citation checking, claim extraction, contradiction detection, SQL result checking)
- Unit, integration, and regression tests
- CI workflow scaffolding

In progress:
- End-to-end pipeline integration
- Query planning module
- Full benchmark evaluation runs
- Error analysis report generation

## Next Milestones

1. **End-to-end pipeline** — connect retrieval, SQL reasoning, planning, and verification into a single query flow
2. **Benchmark execution** — run the full enterprise benchmark through the pipeline and collect metrics
3. **Error analysis** — categorize failures using the taxonomy and produce structured reports
4. **Demo polish** — refine the Streamlit interface for interactive demonstration
