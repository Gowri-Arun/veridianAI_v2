# Veridian AI

Veridian AI is an evaluation-driven enterprise query engine that converts ambiguous business questions into grounded analytical answers using semantic mapping, retrieval, SQL execution, planning, verification, and evaluation.

## Why this project exists

Enterprise teams need reliable answers from a mix of structured and unstructured sources, but business questions are often ambiguous and require careful grounding, validation, and measurement.

## Planned architecture

- Intent understanding
- Semantic mapping
- Planner
- Retrieval
- SQL engine
- Analysis
- Synthesis
- Verification
- Final answer
- Evaluation logging

## Week 1 progress

Week 1 focuses on foundation only:

- repository cleanup
- project scope documentation
- architecture documentation
- failure taxonomy
- benchmark schema
- API skeleton
- Streamlit skeleton
- basic validation scripts
- starter test coverage

## Current status

The repository now includes the Week 1 foundation files, a minimal FastAPI app, a simple Streamlit app, initial benchmark artifacts, and validation/test scaffolding.

## How to run setup

```bash
make setup
```

## How to run API

```bash
make api
```

Then open:

- http://127.0.0.1:8000/health

## How to run UI

```bash
make ui
```

## How to run tests

```bash
pytest
```

## How to validate benchmark

```bash
python scripts/validate_jsonl.py
```

## Week 1 deliverables

- Project scope documentation
- Architecture documentation
- Failure taxonomy
- Benchmark schema
- Benchmark seed data
- FastAPI skeleton
- Streamlit skeleton
- JSONL validation script
- Basic health test

## Roadmap

- Week 1: foundation, docs, benchmark design, API and UI skeleton
- Week 2: data ingestion and schema definitions
- Week 3: deterministic SQL and retrieval scaffolding
- Week 4: evaluation hooks and benchmark execution
- Week 5: end-to-end pipeline implementation
