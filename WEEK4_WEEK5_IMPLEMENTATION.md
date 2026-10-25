# Week 4 and Week 5 Implementation Report

## 1. Previous Repository State

The repository already had synthetic data, ingestion, BM25 retrieval, retrieval evaluation, FastAPI `/api/query`, Streamlit display, and 182 passing tests. SQL-required intents were produced but not consumed, retrieval ignored semantic filters, and `app/sql_engine` was empty.

## 2. Week 4 Work Completed

- Added central metric registry in `app/semantic_layer/metric_registry.py`.
- Added central dimension registry in `app/semantic_layer/dimension_registry.py`.
- Added trusted schema registry in `app/semantic_layer/schema_registry.py`.
- Added typed semantic schemas in `app/schemas/semantic.py`.
- Added typed time normalization in `app/semantic_layer/time_normalizer.py`.
- Added semantic business validation in `app/semantic_layer/validator.py`.
- Refactored semantic parsing into staged deterministic resolution.
- Preserved compatibility keys from the previous parser response.
- Updated retrieval to use canonical query and boost metadata/metric matches.

## 3. Week 5 Work Completed

- Added SQL schemas in `app/schemas/sql.py`.
- Added deterministic structured planner in `app/sql_engine/planner.py`.
- Added SQL compiler in `app/sql_engine/compiler.py`.
- Added safety validator in `app/sql_engine/safety.py`.
- Added read-only DuckDB executor in `app/sql_engine/executor.py`.
- Added comparison calculation in `app/sql_engine/comparison.py`.
- Wired SQL planning, compilation, safety, execution, retrieval, and trace into `/api/query`.
- Updated Streamlit to display query understanding, plan, SQL, parameters, results, evidence, trace, and synthesis status.

## 4. Files Added

- `app/schemas/semantic.py`
- `app/schemas/sql.py`
- `app/semantic_layer/metric_registry.py`
- `app/semantic_layer/dimension_registry.py`
- `app/semantic_layer/schema_registry.py`
- `app/semantic_layer/time_normalizer.py`
- `app/semantic_layer/validator.py`
- `app/sql_engine/planner.py`
- `app/sql_engine/compiler.py`
- `app/sql_engine/safety.py`
- `app/sql_engine/executor.py`
- `app/sql_engine/comparison.py`
- `tests/unit/test_semantic_registries.py`
- `tests/unit/test_time_normalizer.py`
- `tests/unit/test_semantic_parser_week4.py`
- `tests/unit/test_retrieval_semantic_filters.py`
- `tests/unit/test_sql_planner.py`
- `tests/unit/test_sql_compiler_safety.py`
- `tests/integration/test_sql_executor.py`
- `tests/integration/test_query_route_week5.py`
- `WEEK4_WEEK5_IMPLEMENTATION.md`

## 5. Files Modified

- `app/api/query_routes.py`
- `app/agents/intent_agent.py`
- `app/retrieval/retrieval_pipeline.py`
- `app/schemas/query.py`
- `app/schemas/trace.py`
- `app/semantic_layer/semantic_parser.py`
- `frontend/streamlit_app.py`
- `README.md`

## 6. Metric Registry

Supported metrics: `revenue`, `bookings`, `marketing_spend`, `churn`, `customer_count`, `support_tickets`, `pipeline`, `conversion_rate`, `product_usage`, `subscriptions`, and `region_target`.

## 7. Dimension Registry

Supported dimensions: `quarter`, `region`, `segment`, `product`, `channel`, `industry`, `status`, and `severity`.

## 8. Supported Query Shapes

Single metric lookup, grouped metric, period comparison, absolute change, percentage change, multiple independent metrics, top-N grouped metric, and count query.

## 9. Unsupported Query Shapes

Arbitrary joins, arbitrary SQL, general-purpose text-to-SQL, multi-hop reasoning, generated explanations, dense/vector retrieval, hybrid retrieval, reranking, and verification remain out of scope.

## 10. SQL Safety Model

The SQL compiler consumes typed specs only. Identifiers are registry controlled. Values are parameterized. The safety validator rejects mutation keywords, extension loading, file reads, comments, semicolons, unsafe functions, non-SELECT statements, and unknown tables. Execution uses a read-only DuckDB connection.

## 11. DuckDB Execution Design

`DuckDBExecutor` accepts compiled SQL plus parameters, opens the warehouse read-only, fetches bounded rows, records execution timing, returns typed rows/errors, and avoids leaking local filesystem paths in API errors.

## 12. Retrieval Semantic-Filter Changes

Retrieval now accepts `canonical_query`, metric names, and semantic filters. It runs BM25 over the canonical query, expands the candidate set, and applies deterministic score boosts for matching metadata values and related metrics.

## 13. API Changes

`/api/query` now returns typed semantic parse, SQL plan, compiled queries, SQL results, comparison results, retrieved documents, warnings, errors, execution trace, and `synthesis_status = "not_implemented"`.

## 14. Streamlit Changes

The UI now shows query understanding, structured plan, SQL, parameters, SQL results, retrieved evidence, trace, and explicit synthesis-not-implemented messaging. The backend URL uses `VERIDIAN_API_URL` with localhost as default.

## 15. Tests Added

54 new tests were added for registries, time normalization, semantic parsing, retrieval semantic boosts, SQL planning, SQL compilation, safety validation, DuckDB execution, and route integration.

## 16. Commands Run

- `python -m pytest`
- Focused pytest runs for the new semantic, SQL, executor, and route tests.
- `python -m compileall app frontend scripts tests`
- `python -m scripts.validate_week2_data` (failed in this shell because global `python` resolves to MSYS Python without pandas/pydantic/duckdb)
- `python -m scripts.run_retrieval_eval` (failed in this shell because global `python` lacks pydantic)
- `.\.venv\Scripts\python.exe -m scripts.validate_week2_data` (blocked by launcher `Access is denied`)
- `.\.venv\Scripts\python.exe -m scripts.run_retrieval_eval` (blocked by launcher `Access is denied`)
- `python -m pytest tests\integration\test_retrieval_eval.py -q`
- `python -m pytest tests\integration\test_query_route_week5.py::test_sql_lookup_route tests\unit\test_sql_compiler_safety.py::test_safety_rejects_unsafe_sql -q`

## 17. Test Results

Final full suite result: `236 passed`.

Focused verification:

- Retrieval evaluation tests: `18 passed`.
- TestClient-backed API lookup plus read-only safety check: `2 passed`.
- Compile check: passed.

## 18. Retrieval Benchmark Before and After

Before implementation, saved report showed Recall@10 `0.8533`, Hit@10 `0.9200`, MRR `0.6500`.

After implementation, the retrieval evaluator test suite still passes (`18 passed`). The report-generating command could not be executed in this shell because the available global `python` lacks project dependencies and the `.venv` launcher is blocked by `Access is denied`; therefore no new saved retrieval report is claimed.

## 19. Known Limitations

No natural-language synthesis, no LLMs, no verification, no dense/hybrid retrieval, no reranking, no arbitrary SQL, and no production auth/deployment hardening.

## 20. Deferred Week 6 Work

Evidence synthesis, citation validation, claim checking, numeric verification, hallucination detection, confidence calibration, and self-correction should begin in Week 6.

## 21. Architecture Diagram

```text
User query
-> IntentAgent
-> SemanticParser + registries + validator
-> StructuredQueryPlanner
-> SQLCompiler
-> SQLSafetyValidator
-> DuckDBExecutor
-> BM25 RetrievalPipeline when retrieval is required
-> FastAPI typed response
-> Streamlit display
```

## 22. Example Real Query, SQL, Parameters, and Output

Query:

```text
What was enterprise revenue in APAC in Q4 2025?
```

Compiled SQL:

```sql
SELECT SUM(recognized_revenue) AS revenue FROM revenue WHERE region = ? AND segment = ? AND quarter IN (?)
```

Parameters:

```text
["APAC", "Enterprise", "Q4_2025"]
```

Output is returned as a typed `SQLExecutionResult` with columns, rows, row count, and execution timing.
