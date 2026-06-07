# Roadmap

## Phase 1: Repository Foundation and Benchmark Setup

- [x] Repository structure and project configuration
- [x] Project scope documentation
- [x] Architecture documentation
- [x] Failure taxonomy
- [x] Benchmark schema design
- [x] Synthetic enterprise dataset generator
- [x] JSONL validation utility
- [x] Unstructured document validation utility
- [x] FastAPI backend scaffold
- [x] Streamlit frontend scaffold
- [x] Initial test coverage (health, loaders)
- [x] CI workflow scaffolding
- [x] Dockerfile and docker-compose scaffolding

## Phase 2: Ingestion and Metadata Pipeline

- [x] Document loading (Markdown with YAML frontmatter)
- [x] Text chunker with overlap
- [x] Metadata extraction
- [x] Table loader module
- [x] DuckDB warehouse build
- [x] Schema snapshot generation
- [x] Table profiling
- [x] Structured data validation

## Phase 3: Retrieval and SQL Reasoning

- [x] BM25 retriever
- [x] Dense embedding retriever
- [x] FAISS vector index build
- [x] Hybrid retrieval fusion
- [x] Query rewriting module
- [x] Cross-encoder re-ranker
- [x] Citation builder
- [ ] End-to-end retrieval pipeline integration

- [x] SQL engine with schema context
- [x] SQL validation and error taxonomy
- [x] DuckDB client module
- [x] LLM-based SQL generation
- [x] Template SQL support
- [x] Result interpreter
- [ ] Deterministic SQL reasoning path (in progress)

## Phase 4: Planning, Semantic Layer, and Verification

- [x] Semantic layer — metric registry
- [x] Semantic layer — dimension registry
- [x] Semantic layer — synonym mapper
- [x] Semantic layer — region normalizer
- [x] Semantic layer — time normalizer
- [x] Semantic layer — business rules
- [x] Semantic layer — schema mapper
- [x] Semantic layer — semantic parser

- [x] Verification — citation checker
- [x] Verification — claim extractor
- [x] Verification — contradiction checker
- [x] Verification — numeric claim checker
- [x] Verification — SQL result checker
- [x] Verification — confidence calibrator
- [x] Verification — answer reviser
- [x] Verification — verifier pipeline

- [ ] Query planner — full integration
- [ ] Plan critic agent

## Phase 5: Evaluation, Reports, and Demo Polish

- [x] Evaluation — benchmark loader
- [x] Evaluation — retrieval metrics
- [x] Evaluation — SQL metrics
- [x] Evaluation — plan evaluation
- [x] Evaluation — faithfulness evaluation
- [x] Evaluation — hallucination evaluation
- [x] Evaluation — citation evaluation
- [x] Evaluation — latency evaluation
- [x] Evaluation — cost evaluation
- [x] Evaluation — answer evaluation
- [x] Evaluation — ablation runner
- [x] Evaluation — regression runner
- [x] Evaluation — report generator
- [ ] End-to-end benchmark evaluation run
- [ ] Error analysis report generation

- [x] Frontend — Query Engine page
- [x] Frontend — Execution Trace page
- [x] Frontend — Evaluation Dashboard page
- [x] Frontend — Failure Analysis page
- [x] Frontend — Ablation Results page
- [ ] Polished demo interface

## Phase 6: Ongoing Improvement

- [ ] Workflow orchestration (LangGraph)
- [ ] Fallback workflow logic
- [ ] Trace recording module
- [ ] Full CI pipeline
- [ ] Expanded test coverage
- [ ] Performance optimization
