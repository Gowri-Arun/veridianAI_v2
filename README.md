# Veridian AI

Veridian AI is an evaluation-driven enterprise query engine that converts ambiguous business questions into grounded analytical answers using intent classification, semantic mapping, retrieval, SQL reasoning, planning, verification, and evaluation. Designed around reproducibility, modular pipelines, and benchmark-driven development.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Status-In%20Progress-yellow" alt="Status">
</p>

## Status

**Status: In progress**

Current stage (Week 3):
- Intent classification (rule-based, 11 query types)
- Semantic mapping (synonym normalization, canonical query generation)
- BM25 retrieval (deterministic scoring, real-time ranking)
- `/api/query` pipeline wired end-to-end
- Frontend trace display with intent, semantic mapping, and retrieval visualization

## Why Veridian AI

Enterprise question answering is difficult because business questions are often ambiguous, require evidence from both documents and structured data, and need grounded answers rather than fluent guesses. A system that cannot explain how it arrived at an answer or cite its sources is not suitable for enterprise use.

Veridian AI separates the pipeline into ingestion, intent classification, semantic mapping, retrieval, SQL reasoning, planning, verification, and evaluation so that answers can be tested, measured, and improved systematically.

## System Overview

```
Implemented (Week 3):
User Question
→ Intent Classification
→ Semantic Mapping
→ BM25 Document Retrieval
→ Structured API Response
→ Frontend Trace Display

Planned (Weeks 4-5):
→ SQL / Structured Data Reasoning
→ Evidence Collection
→ Answer Generation
→ Verification
→ Evaluation Report
```

The architecture is modular and evaluation-first. Each component can be developed, tested, and benchmarked independently.

## What This Project Demonstrates

- Building an AI system beyond a simple chatbot
- Designing an evaluation-first architecture for enterprise question answering
- Rule-based intent classification without relying on LLM calls
- Semantic synonym mapping for canonical query normalization
- BM25 deterministic retrieval over document chunks
- Designed to combine retrieval over documents with structured SQL-style reasoning in later stages
- Creating synthetic benchmark data for repeatable testing
- Separating ingestion, retrieval, planning, execution, verification, and reporting
- Using FastAPI, Streamlit, tests, Docker, and Makefile-based workflows

## Repository Structure

| Path | Purpose |
| --- | --- |
| `app/` | Backend application code and API modules |
| `frontend/` | Streamlit user interface |
| `benchmarks/` | Benchmark schema and evaluation assets |
| `data/` | Synthetic enterprise documents, tables, chunks, and metadata |
| `docs/` | Architecture, project scope, failure taxonomy, and study notes |
| `experiments/` | Experiment outputs and development runs |
| `reports/` | Generated reports and analysis artifacts |
| `scripts/` | Utility scripts for validation, ingestion, and setup |
| `tests/` | Unit and integration tests |
| `configs/` | Configuration files |
| `.github/workflows/` | CI workflow definitions |

## Pipeline Components (Week 3)

### Intent Classification (`app/agents/intent_agent.py`)
Rule-based regex classifier recognizing 11 query types: `simple_document`, `simple_sql`, `metric_lookup`, `comparison`, `trend_analysis`, `hybrid_sql_document`, `root_cause_analysis`, `ambiguous`, `unanswerable`, `contradiction`, `adversarial`. Extracts metrics, dimensions, and filters from the query text.

### Semantic Mapping (`app/semantic_layer/`)
- **Synonym Mapper** — normalizes raw query terms to canonical metrics (e.g., "sales" → `revenue`), regions, segments, and time periods
- **Semantic Parser** — produces a `canonical_query`, mapped terms, extracted metrics/filters, and confusion warnings

### BM25 Retrieval (`app/retrieval/`)
- **BM25 Retriever** — deterministic scoring over 120 document chunks using `app/schemas/retrieval.py:RetrievedChunk`
- **Retrieval Pipeline** — wrapper for the BM25 retriever

### Query API (`app/api/query_routes.py`)
- `POST /api/query` — accepts `QueryRequest(query, top_k, include_trace)`, returns `QueryResponse` with intent classification, semantic mapping, retrieved documents, and execution trace

## Current Progress

### Completed
- Project scope and architecture documentation
- Failure taxonomy and benchmark schema
- Synthetic enterprise benchmark dataset (120 chunks, 20 documents)
- Document ingestion pipeline with chunking and metadata extraction
- Schema snapshot generation
- JSONL validation utility
- Initial tests and CI scaffolding
- **Intent classification** — rule-based with 11 query types
- **Semantic mapping** — synonym normalization and canonical query generation
- **BM25 retrieval** — deterministic document scoring and ranking
- **Query API** — real `/api/query` pipeline with trace support

### In Progress
- SQL reasoning module (Week 4)
- Query planning module (Week 4)
- Analysis pipeline (Week 4)
- Answer synthesis (Week 5)
- Verification layer (Week 5)
- End-to-end evaluation runner (Week 5)

## Tech Stack

**Backend:**
- Python 3.11+
- FastAPI
- Pydantic
- Uvicorn

**Frontend:**
- Streamlit

**Retrieval / Search:**
- BM25 scoring (deterministic, built-in)

**Evaluation:**
- (Planned for future weeks)

**Data / Benchmark:**
- JSONL
- Synthetic enterprise benchmark with narratives
- YAML config files

**Engineering:**
- Docker
- docker-compose
- Makefile
- pytest
- GitHub Actions

## Quickstart

```bash
git clone https://github.com/Gowri-Arun/veridianAI_v2.git
cd veridianAI_v2
python -m venv .venv
```

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

### Run tests

```bash
pytest
```

### Start the API

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/health

### Start the frontend

```bash
streamlit run frontend/streamlit_app.py
```

## Development Workflow

1. Run tests — `pytest`
2. Start backend — `uvicorn app.main:app --reload`
3. Start frontend — `streamlit run frontend/streamlit_app.py`
4. Send queries via `POST /api/query`

## Evaluation Philosophy

Veridian AI is built around evaluation, not demo quality. The system is designed to support:

- **Answer grounding** — every claim should trace back to retrieved evidence or SQL results
- **Failure taxonomy** — a structured classification of failure modes (retrieval, SQL, synthesis, citation, etc.)
- **Benchmark examples** — curated queries with known traps, unanswerable cases, and adversarial inputs
- **Reproducible test cases** — unit, integration, and regression tests for each component
- **Planned verification layer** — deterministic checks for citations, numeric claims, contradictions, and SQL validity

## Roadmap

- [x] Repository foundation
- [x] Synthetic enterprise dataset
- [x] Ingestion pipeline
- [x] Chunk and metadata generation
- [x] Intent classification
- [x] Semantic mapping
- [x] BM25 retrieval
- [x] Query API
- [ ] SQL reasoning module
- [ ] Query planner / analysis
- [ ] Answer synthesis
- [ ] Verification layer
- [ ] End-to-end evaluation runner
- [ ] Polished demo interface

## Positioning

This project is intended as a practical exploration of reliable enterprise AI systems, with emphasis on grounded answers, modular design, and measurable evaluation.
