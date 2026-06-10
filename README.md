# Veridian AI

Veridian AI is an evaluation-driven enterprise query engine that converts ambiguous business questions into grounded analytical answers using retrieval, SQL reasoning, planning, verification, and evaluation. Designed around reproducibility, modular pipelines, and benchmark-driven development.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Status-In%20Progress-yellow" alt="Status">
</p>

## Status

**Status: In progress**

Current stage:
- Repository foundation complete
- FastAPI backend scaffolded
- Streamlit frontend scaffolded
- Synthetic enterprise benchmark created
- Ingestion pipeline implemented
- Document chunks, metadata, and schema snapshots generated
- Retrieval, SQL reasoning, planning, and verification layers under development

## Why Veridian AI

Enterprise question answering is difficult because business questions are often ambiguous, require evidence from both documents and structured data, and need grounded answers rather than fluent guesses. A system that cannot explain how it arrived at an answer or cite its sources is not suitable for enterprise use.

Veridian AI separates the pipeline into ingestion, retrieval, SQL reasoning, planning, verification, and evaluation so that answers can be tested, measured, and improved systematically.

## System Overview

```
User Question
→ Query Understanding / Planning
→ Document Retrieval
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
- Combining retrieval over documents with structured SQL-style reasoning
- Creating synthetic benchmark data for repeatable testing
- Separating ingestion, retrieval, planning, execution, verification, and reporting
- Using FastAPI, Streamlit, tests, Docker, and Makefile-based workflows
- Writing documentation for reproducibility and system design

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

## Current Progress

### Completed
- Project scope and architecture documentation
- Failure taxonomy and benchmark schema
- FastAPI backend scaffold
- Streamlit UI scaffold
- Synthetic enterprise benchmark dataset
- JSONL validation utility
- Document ingestion pipeline
- Chunking and metadata extraction
- Schema snapshot generation
- Initial tests and CI scaffolding

### In Progress
- Retrieval pipeline
- Deterministic SQL reasoning path
- Query planning module
- Verification layer
- End-to-end benchmark evaluation
- Report generation and error analysis

## Tech Stack

**Backend:**
- Python 3.11+
- FastAPI
- Pydantic
- DuckDB (analytics engine)
- Uvicorn

**Frontend:**
- Streamlit

**Retrieval / Search:**
- BM25 indexing
- FAISS vector index
- Dense embeddings
- Hybrid retrieval pipeline
- Cross-encoder re-ranker

**Evaluation:**
- Answer faithfulness evaluation
- Retrieval precision / recall
- SQL correctness validation
- Citation checking
- Hallucination detection
- Latency and cost tracking
- Ablation framework

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

### Run validation scripts

```bash
python scripts/validate_jsonl.py
python scripts/validate_unstructured_docs.py
```

### Generate synthetic data (if not present)

```bash
python scripts/generate_synthetic_data.py
```

### Run ingestion

```bash
python scripts/ingest_documents.py
python scripts/build_duckdb.py
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

1. Validate data — `python scripts/validate_jsonl.py`
2. Generate structured data — `python scripts/generate_synthetic_data.py`
3. Ingest documents — `python scripts/ingest_documents.py`
4. Build warehouse — `python scripts/build_duckdb.py`
5. Run tests — `pytest`
6. Start backend — `uvicorn app.main:app --reload`
7. Start frontend — `streamlit run frontend/streamlit_app.py`
8. Inspect generated artifacts in `data/processed/`

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
- [ ] Retrieval pipeline
- [ ] SQL reasoning module
- [ ] Query planner
- [ ] Answer verification layer
- [ ] End-to-end evaluation runner
- [ ] Error analysis reports
- [ ] Polished demo interface

## Positioning

This project is intended as a practical exploration of reliable enterprise AI systems, with emphasis on grounded answers, modular design, and measurable evaluation.
