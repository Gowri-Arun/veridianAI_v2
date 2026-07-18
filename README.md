# Veridian AI

Veridian AI is a deterministic enterprise analytics prototype built around a local synthetic warehouse and a small corpus of internal documents.

**Current reality:** Veridian AI currently supports controlled deterministic analytical queries over a local DuckDB warehouse. It does not yet provide general-purpose text-to-SQL, LLM-generated answers, evidence synthesis, or verification.

## Implemented Architecture

```text
User query
-> FastAPI /api/query
-> rule-based intent classification
-> registry-backed semantic parsing
-> semantic validation
-> deterministic SQL planning when SQL is required
-> trusted SQL compilation
-> read-only SQL safety validation
-> DuckDB execution
-> optional BM25 document retrieval
-> typed API response
-> Streamlit trace/results display
```

For hybrid-style questions, the API returns both SQL results and retrieved document chunks. It explicitly returns `synthesis_status = "not_implemented"` and does not fabricate a final explanation.

## What Works

- Synthetic structured data across 9 CSV tables.
- 20 Markdown documents and 120 processed document chunks.
- Local DuckDB warehouse at `data/warehouse/veridian.duckdb`.
- CSV and Markdown ingestion, metadata extraction, and section-aware chunking.
- BM25 retrieval with semantic query/filter boosts.
- Retrieval evaluation with Recall@K, Hit Rate@K, and MRR.
- Metric, dimension, and schema registries grounded in the actual warehouse.
- Typed time normalization for Q1-Q4 2025.
- Deterministic semantic validation with typed errors.
- Deterministic SQL planning for a limited set of supported query shapes.
- SQL compilation from trusted registry identifiers only.
- Parameterized values and read-only DuckDB execution.
- FastAPI and Streamlit integration for semantic parse, SQL plan, SQL, parameters, results, retrieved evidence, and trace.

## Supported Metrics

| Metric | Table | Column | Default aggregation |
|---|---|---|---|
| `revenue` | `revenue` | `recognized_revenue` | `sum` |
| `bookings` | `revenue` | `bookings` | `sum` |
| `marketing_spend` | `marketing_spend` | `spend` | `sum` |
| `churn` | `churn` | `churn_rate` | `avg` |
| `customer_count` | `customers` | `customer_id` | `count` |
| `support_tickets` | `support_tickets` | `ticket_id` | `count` |
| `pipeline` | `sales_pipeline` | `pipeline_value` | `sum` |
| `conversion_rate` | `sales_pipeline` | `conversion_rate` | `avg` |
| `product_usage` | `product_usage` | `usage_score` | `avg` |
| `subscriptions` | `subscriptions` | `subscription_id` | `count` |
| `region_target` | `region_targets` | `revenue_target` | `sum` |

## Supported Dimensions

`quarter`, `region`, `segment`, `product`, `channel`, `industry`, `status`, and `severity`, with allowed values defined in `app/semantic_layer/dimension_registry.py`.

## Supported Query Shapes

- Single metric lookup: `What was enterprise revenue in APAC in Q4 2025?`
- Grouped metric: `Show revenue by region in Q4 2025.`
- Period comparison: `Compare APAC enterprise revenue in Q3 and Q4 2025.`
- Absolute change: `How much did APAC enterprise revenue decline from Q3 to Q4 2025?`
- Percentage change: `What was the percentage change in APAC enterprise revenue from Q3 to Q4 2025?`
- Multiple independent metrics: `Compare revenue and marketing spend in APAC in Q4 2025.`
- Top-N grouped metric: `Which regions had the highest revenue in Q4 2025?`
- Count query: `How many enterprise customers are in APAC?`

Unsupported query shapes return typed errors or unsupported planning results instead of arbitrary generated SQL.

## SQL Safety Model

- SQL specs are generated from typed semantic output, never raw user text.
- Table and column identifiers come only from trusted registries.
- User values are passed as DuckDB parameters.
- Only compiler-generated `SELECT` statements are accepted.
- Safety validation rejects mutation, extension loading, file reads, comments, semicolons, multiple statements, unknown tables, and unsafe functions.
- DuckDB is opened in read-only mode for runtime execution.

## API Response

`POST /api/query` returns:

- `intent`
- `semantic_parse`
- `sql_plan`
- `compiled_queries`
- `sql_results`
- `comparison_results`
- `retrieved_documents`
- `warnings`
- `errors`
- `execution_trace`
- `synthesis_status`

Legacy fields `semantic_mapping` and `trace` are retained for compatibility.

## Streamlit UI

Run the UI to see separate sections for query understanding, structured query plan, generated SQL, parameters, SQL results, retrieved evidence, execution trace, and synthesis status. Raw evidence is not presented as a final answer.

## Setup

Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Unix/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Start the backend:

```bash
python -m uvicorn app.main:app --reload
```

Start the frontend:

```bash
python -m streamlit run frontend/streamlit_app.py
```

Optional backend URL override:

```bash
VERIDIAN_API_URL=http://127.0.0.1:8000 python -m streamlit run frontend/streamlit_app.py
```

Run tests and validation:

```bash
python -m pytest
python -m compileall app frontend scripts tests
python -m scripts.validate_week2_data
python -m scripts.run_retrieval_eval
python -m scripts.validate_sql_benchmark
python -m scripts.run_sql_eval
python -m scripts.inspect_duckdb_schema
```

Week 6 benchmark outputs are written to:

- `experiments/results/sql_eval_results.json`
- `experiments/results/sql_eval_results.csv`
- `reports/sql_benchmark_report.md`

Environment checks and setup helpers:

```bash
python -m scripts.check_environment
./scripts/bootstrap.sh
```

Windows PowerShell:

```powershell
.\scripts\bootstrap.ps1
```

Docker Compose expects environment values from `.env`. If using Compose, copy `.env.example` to `.env` first.

## Week 6 SQL Benchmark

The SQL benchmark lives in `benchmarks/sql_gold.jsonl` and contains 57 deterministic cases across metric lookup, grouping, period comparison, absolute change, percentage change, multiple metrics, top-N, counts, ambiguity, unsupported shapes, and adversarial requests.

The evaluator does not use an LLM judge and does not generate synthetic natural-language answers. It compares typed semantic parse fields, deterministic SQL plans, trusted identifiers, parameterization, read-only safety behavior, DuckDB execution, result shape, and comparison direction.

## Limitations

- No LLM-generated SQL.
- No OpenAI, Anthropic, LangChain, or LangGraph integration.
- No vector retrieval, hybrid retrieval, or reranking.
- No natural-language answer synthesis.
- No hallucination verification or self-correction.
- No arbitrary SQL execution endpoint.
- No authentication or production deployment hardening.
