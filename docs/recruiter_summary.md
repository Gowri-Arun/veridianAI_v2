# Veridian AI — Recruiter Summary

## What It Is

Veridian AI is an evaluation-driven enterprise query engine. It converts ambiguous business questions into grounded analytical answers using retrieval, SQL reasoning, planning, verification, and evaluation. It is not a chatbot — it is a modular pipeline designed for reliability and measurability.

## Why It Is Technically Meaningful

Most AI demo projects stop at a prompt wrapper or a simple RAG chain. Veridian AI goes further by separating the problem into distinct engineering modules:

- **Hybrid retrieval** — BM25, dense embeddings, FAISS indexing, cross-encoder re-ranking, and query rewriting
- **Structured data reasoning** — schema-aware SQL generation, validation, execution, and result interpretation using DuckDB
- **Semantic layer** — business term resolution, synonym mapping, metric and dimension registries, time/region normalization
- **Verification** — deterministic checks for citations, contradictions, numeric claims, SQL results, and confidence calibration
- **Evaluation framework** — benchmark loading, retrieval/SQL/faithfulness/hallucination/citation/latency/cost evaluation, ablation experiments, and report generation
- **Workflow orchestration** — LangGraph-based pipeline with trace recording and fallback logic

## What Engineering Skills It Demonstrates

- **System design** — modular architecture with clear separation of concerns
- **Python engineering** — FastAPI, Pydantic, Streamlit, pandas, DuckDB
- **Search and retrieval** — BM25, embeddings, FAISS, hybrid fusion, re-ranking
- **LLM application** — prompt engineering, structured outputs, token management, evaluation
- **SQL and data engineering** — schema management, query validation, warehouse build
- **Testing** — pytest unit, integration, and regression tests
- **DevOps** — Docker, Makefile, GitHub Actions, YAML configuration
- **Documentation** — architecture docs, failure taxonomy, benchmark schema, evaluation methodology

## Current Stage

The repository contains a complete backend scaffold, a multi-page Streamlit frontend, a synthetic enterprise benchmark dataset (with embedded business narratives), a full ingestion pipeline, and extensive evaluation infrastructure. Retrieval, SQL reasoning, and verification modules are implemented. Query planning and end-to-end pipeline integration are in progress.

## How It Differs from a Basic Chatbot

- Every component has corresponding tests and evaluation metrics
- Claims are grounded in retrieved evidence and SQL results, not generated from model parameters alone
- A verification layer checks citations, contradictions, and numeric accuracy before answers are returned
- The system distinguishes answerable questions from unanswerable ones
- A failure taxonomy classifies errors so they can be measured and addressed systematically
- Ablation experiments allow measuring the impact of each component on overall performance
