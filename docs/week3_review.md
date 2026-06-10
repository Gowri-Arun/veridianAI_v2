# Week 3 Review — First Deterministic Query Pipeline

## What Was Done

Week 3 delivered Veridian AI's first no-LLM query-intelligence slice: intent classification, semantic mapping, BM25 retrieval, and a real `/api/query` endpoint — all without any LLM calls, vector stores, or external AI services.

### Implemented Components

| Component | Module | Status |
|---|---|---|
| Pydantic Schemas | `app/schemas/{query,intent,retrieval,trace}.py` | Done — 5 models |
| Intent Classifier | `app/agents/intent_agent.py` | Done — 11 query types, rule-based |
| Synonym Mapper | `app/semantic_layer/synonym_mapper.py` | Done — 40+ synonym mappings across 4 categories |
| Semantic Parser | `app/semantic_layer/semantic_parser.py` | Done — canonical query, mapped terms, confusion warnings |
| BM25 Retriever | `app/retrieval/bm25_retriever.py` | Done — deterministic scoring, 120-chunk corpus |
| Retrieval Pipeline | `app/retrieval/retrieval_pipeline.py` | Done — BM25 wrapper |
| Query API | `app/api/query_routes.py` | Done — `POST /api/query` |
| Frontend Trace | `frontend/streamlit_app.py` | Done — live intent/mapping/retrieval display |

### Test Coverage

| Test File | Count |
|---|---|
| `tests/unit/test_query_schemas.py` | 12 tests |
| `tests/unit/test_intent_agent.py` | 16 tests |
| `tests/unit/test_semantic_mapper.py` | 18 tests |
| `tests/unit/test_bm25_retriever.py` | 8 tests |
| `tests/integration/test_query_route.py` | 6 tests |
| **Total new** | **60 tests** |
| + Existing tests | 72 tests |
| **Grand total** | **132 tests** |

### Intent Classification Coverage

- `simple_document` — definition/explanation queries
- `simple_sql` — structured data queries
- `metric_lookup` — single metric value queries
- `comparison` — comparative queries (vs, between)
- `trend_analysis` — change-over-time queries
- `hybrid_sql_document` — needs both docs and SQL
- `root_cause_analysis` — causal why/reason queries
- `ambiguous` — vague or under-specified queries
- `unanswerable` — attribution-to-person queries
- `contradiction` — conflicting-information queries
- `adversarial` — injection/override attempts

### Architectural Decisions

1. **No LLM dependency** — all components are deterministic (regex, math, rule-based)
2. **No `rank_bm25` package** — implemented BM25 from scratch to avoid external dep
3. **Pydantic v2** — `model_dump()` for serialization
4. **Trace-first** — every pipeline step records structured trace metadata for debugging
5. **Intent drives retrieval** — only queries classified as needing document evidence hit BM25
6. **Synonym map is comprehensive but curated** — 40+ entries focused on enterprise metrics, regions, segments

### File Changes Summary

| Action | Files |
|---|---|
| Created | `app/schemas/query.py`, `app/schemas/intent.py`, `app/schemas/retrieval.py`, `app/schemas/trace.py` |
| Created | `app/agents/intent_agent.py` |
| Created | `app/semantic_layer/synonym_mapper.py`, `app/semantic_layer/semantic_parser.py` |
| Created | `app/retrieval/bm25_retriever.py`, `app/retrieval/retrieval_pipeline.py` |
| Rewritten | `app/api/query_routes.py`, `frontend/streamlit_app.py`, `README.md` |
| Fixed | `app/main.py` (removed duplicate prefix on router include) |
| Created | `tests/unit/test_query_schemas.py`, `tests/unit/test_intent_agent.py`, `tests/unit/test_semantic_mapper.py`, `tests/unit/test_bm25_retriever.py` |
| Created | `tests/integration/test_query_route.py` |
| Created | `docs/week3_review.md` |

### What Was NOT Done (Deferred)

- SQL reasoning / DuckDB execution
- Query planning / analysis module
- Answer synthesis (no LLM, no template-based generation)
- Verification layer (citation checks, contradiction detection)
- Evaluation dashboard / benchmark runner
- Vector / hybrid / cross-encoder retrieval
- Multi-turn conversation
- Authentication / rate limiting

### Test Results

All 132 tests pass:
```
pytest — 132 passed (72 existing + 60 new)
```

### Next Up (Week 4)

- SQL reasoning module — deterministic SQL generation from intent+semantic output
- DuckDB query execution against the built warehouse
- Analysis pipeline — metric calculation, comparison, trend detection
- Integration of SQL results into the query response
- Evaluation harness for SQL correctness
