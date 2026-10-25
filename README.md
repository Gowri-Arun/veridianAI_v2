# Veridian AI

> **Deterministic, explainable analytics over structured enterprise data and internal documents.**

Veridian AI is a full-stack enterprise analytics prototype that turns a supported set of natural-language business questions into validated semantic representations, trusted SQL plans, and read-only DuckDB results. A separate BM25 retrieval path surfaces relevant internal-document excerpts, while a Streamlit interface exposes the complete execution trace.

Unlike unconstrained text-to-SQL systems, Veridian uses a registry-backed, deterministic pipeline: user input never becomes an arbitrary executable SQL statement. The current system returns structured results and retrieved evidence; natural-language answer synthesis and evidence verification are not implemented.

---

## Highlights

* **Constrained Query Execution:** Typed semantic parsing, registry-backed identifiers, parameterized SQL, SQL safety validation, and read-only DuckDB access.
* **Inspectable Decisions:** View recognized intent, semantic parse, query plan, generated SQL, parameters, results, retrieved documents, and stage-by-stage traces.
* **Document Retrieval:** BM25 ranking over section-aware Markdown chunks, with metadata-based boosts and reproducible ranking evaluation.
* **Explicit Failure Handling:** Unsupported or ambiguous questions return typed clarification or error states instead of speculative SQL or invented answers.
* **Local-First Development:** FastAPI backend, Streamlit frontend, synthetic warehouse, and reproducible evaluation scripts.

---

## Measured Results

### Analytical Correctness: Before and After the Count-Query Fix
A 50-case local benchmark compared an earlier repository commit (`b4d1d1821d08a66d1660eb2d9d849277d71014f6`) with the updated intent classifier and semantic parser. Expected outputs for the 38 executable questions were computed using independently authored, parameterized reference SQL against the same DuckDB warehouse.

| Measure | Before | After |
| :--- | :--- | :--- |
| **Exact result matches on executable queries** | 29/38 (76.3%) | 35/38 (92.1%) |
| **Correct clarification controls** | 5/5 | 5/5 |
| **Adversarial prompts causing SQL execution** | 0/7 | 0/7 |
| **Median typed-response latency** | 48.9 ms | 35.8 ms |
| **p95 typed-response latency** | 227.6 ms | 177.8 ms |

> **Impact:** The parsing changes recovered six count-oriented queries, improving exact-match correctness by 15.8 percentage points on this fixed benchmark. The observed latency decrease is not attributed causally to the parser fix: timings were in-process, local, and subject to connection and run-to-run variation. The evaluation included five warm latency repetitions per executable question.

*Note: Three executable cases remained incorrect, involving bookings and conversion-rate questions. This benchmark measures typed-response execution, not natural-language answer generation or production accuracy.*

#### Reproduce the Current Benchmark
```bash
python scripts/run_analytical_correctness_benchmark.py --latency-repetitions 5
```
*For an earlier-commit comparison, use an isolated Git worktree and the script's `--source-root` option; see the script for its supported arguments.*

### Retrieval Ranking
On a separate 25-query synthetic relevance benchmark, metadata-assisted BM25 increased MRR from **0.6500 to 0.7733 (+19.0%)** versus raw lexical BM25. Recall@3 increased from **0.6500 to 0.7000**, while Recall@10 decreased from **0.8533 to 0.7833**. The metadata boosts therefore improved early ranking on this evaluation, not every retrieval metric.

*These are local synthetic evaluations, not production-user outcomes or claims of general benchmark superiority.*

---

## Architecture

```text
Business question
      |
      v
FastAPI  POST /api/query
      |
      v
Rule-based intent classification
      |
      v
Registry-backed semantic parsing and validation
      |
      +------------------------+
      |                        |
      v                        v
Deterministic SQL path     BM25 document path (when applicable)
      |                        |
Typed query plan          Metadata-aware retrieval
      |                        |
Trusted SQL compiler      Ranked source chunks
      |                        |
Read-only SQL validator       |
      |                        |
DuckDB execution              |
      |                        |
      +------------+-----------+
                   |
                   v
       Typed response + execution trace
                   |
                   v
             Streamlit UI
```

For questions requiring both structured and documentary evidence, the API returns SQL results and retrieved chunks side by side. It does not combine them into a synthesized explanation; `synthesis_status` is `not_implemented`.

---

## Supported Capabilities

### Structured Data
The included development dataset consists of **9 CSV-backed warehouse tables** with a local DuckDB database at `data/warehouse/veridian.duckdb`. The documentary corpus contains **20 Markdown documents**, processed into **120 chunks**.

The semantic layer maintains trusted metric, dimension, and schema registries. Supported dimensions include **quarter**, **region**, **segment**, **product**, **channel**, **industry**, **status**, and **severity**, subject to the allowed values and table mappings in the registries.

| Metric | Source Table | Source Column | Aggregation |
| :--- | :--- | :--- | :--- |
| **revenue** | `revenue` | `recognized_revenue` | `SUM` |
| **bookings** | `revenue` | `bookings` | `SUM` |
| **marketing_spend** | `marketing_spend` | `spend` | `SUM` |
| **churn** | `churn` | `churn_rate` | `AVG` |
| **customer_count** | `customers` | `customer_id` | `COUNT` |
| **support_tickets** | `support_tickets` | `ticket_id` | `COUNT` |
| **pipeline** | `sales_pipeline` | `pipeline_value` | `SUM` |
| **conversion_rate** | `sales_pipeline` | `conversion_rate` | `AVG` |
| **product_usage** | `product_usage` | `usage_score` | `AVG` |
| **subscriptions** | `subscriptions` | `subscription_id` | `COUNT` |
| **region_target** | `region_targets` | `revenue_target` | `SUM` |

### Example Questions
*These illustrate supported query shapes, not a guarantee that every phrasing or combination succeeds:*

| Query Shape | Example |
| :--- | :--- |
| **Metric lookup** | What was enterprise revenue in APAC in Q4 2025? |
| **Grouping** | Show revenue by region in Q4 2025. |
| **Period comparison** | Compare APAC enterprise revenue in Q3 and Q4 2025. |
| **Absolute change** | How much did APAC enterprise revenue decline from Q3 to Q4 2025? |
| **Percentage change** | What was the percentage change in APAC enterprise revenue from Q3 to Q4 2025? |
| **Multiple metrics** | Compare revenue and marketing spend in APAC in Q4 2025. |
| **Top-N / ranking** | Which regions had the highest revenue in Q4 2025? |
| **Qualified count** | How many enterprise customers are in APAC? |

*Time normalization currently covers Q1–Q4 2025. Unsupported query shapes return typed errors or clarification states rather than arbitrary SQL.*

---

## SQL Safety by Design

1. **Trusted Identifiers:** Tables, columns, and metrics are selected from maintained registries, not copied directly from user input.
2. **Parameterized Values:** Filters and other user-supplied values are bound as DuckDB parameters.
3. **Compiler-Controlled SQL:** Only SQL generated by the deterministic planner/compiler is eligible for execution.
4. **Statement Validation:** The safety layer restricts execution to permitted `SELECT` statements and rejects mutations, unknown identifiers, unsafe functions, file access, extension loading, comments, semicolons, and multiple statements.
5. **Read-Only Database Access:** Runtime DuckDB connections are opened in read-only mode.

*The adversarial benchmark confirmed zero SQL executions for seven tested adversarial inputs. This is a limited local safety result, not a formal security guarantee.*

---

## Technology Stack

| Layer | Technology |
| :--- | :--- |
| **API** | Python, FastAPI |
| **Analytics Engine** | DuckDB, parameterized SQL |
| **Query Interpretation** | Deterministic intent classification, semantic registries, typed planning |
| **Document Retrieval** | BM25, metadata-aware scoring |
| **Interface** | Streamlit |
| **Evaluation** | `pytest`, independently authored SQL references, retrieval metrics |

---

## Getting Started

### Prerequisites
* Python and a compatible environment for `requirements.txt`
* The repository's local dataset and warehouse artifacts, or its data-preparation workflow

### Installation

#### Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

#### macOS / Linux
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Running the System

1. **Run the API Backend:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. **Run the Streamlit UI:**
   In another terminal with the virtual environment activated:
   ```bash
   python -m streamlit run frontend/streamlit_app.py
   ```

*The default API URL is `http://127.0.0.1:8000`. To override it:*

* **PowerShell:**
  ```powershell
  $env:VERIDIAN_API_URL = "http://127.0.0.1:8000"
  python -m streamlit run frontend/streamlit_app.py
  ```
* **macOS / Linux:**
  ```bash
  VERIDIAN_API_URL=http://127.0.0.1:8000 python -m streamlit run frontend/streamlit_app.py
  ```

The interface displays query interpretation, SQL plan, generated SQL, parameters, execution results, document evidence, and execution trace separately. Retrieved excerpts are not presented as a synthesized final answer.

---

## API Contract

`POST /api/query` returns a typed response with fields including:

```json
{
  "intent": "...",
  "semantic_parse": "...",
  "sql_plan": "...",
  "compiled_queries": "...",
  "sql_results": "...",
  "comparison_results": "...",
  "retrieved_documents": "...",
  "warnings": "...",
  "errors": "...",
  "execution_trace": "...",
  "synthesis_status": "..."
}
```

The compatibility fields `semantic_mapping` and `trace` are also retained. Exact response values depend on whether the question is supported, requires clarification, or invokes structured and/or document retrieval.

---

## Evaluation and Development

### Analytical Correctness Regression
```bash
python -m pytest tests/unit/test_intent_agent.py tests/unit/test_semantic_parser_week4.py tests/integration/test_customer_count_query.py -q
python scripts/run_analytical_correctness_benchmark.py --latency-repetitions 5
```
The newer 50-case analytical benchmark includes 38 executable queries, 5 clarification controls, and 7 adversarial controls. It evaluates exact outputs against independently written SQL, rather than using the application's generated SQL as its own ground truth.

### Existing SQL Benchmark
The separate Week 6 benchmark in `benchmarks/sql_gold.jsonl` contains 57 deterministic cases spanning lookups, grouping, comparisons, changes, multi-metric questions, top-N, counts, ambiguity, unsupported queries, and adversarial requests. It evaluates semantic parses, plans, safe compilation, execution behavior, result shapes, and comparison direction—not generated prose.

```bash
python -m scripts.validate_sql_benchmark
python -m scripts.run_sql_eval
```

**Generated Outputs:**
* `experiments/results/sql_eval_results.json`
* `experiments/results/sql_eval_results.csv`
* `reports/sql_benchmark_report.md`

### Retrieval Evaluation and Additional Checks
```bash
python -m pytest
python -m scripts.validate_week2_data
python -m scripts.run_retrieval_eval
python -m scripts.inspect_duckdb_schema
python -m scripts.check_environment
```

Bootstrap helpers are also available at `scripts/bootstrap.sh` and `scripts/bootstrap.ps1`. If using Docker Compose, copy `.env.example` to `.env` and configure its required values first.

---

## Current Limitations

* **Not General-Purpose Text-to-SQL:** Only implemented query shapes and registered data concepts are supported.
* **No LLM-Generated SQL or Answers:** No OpenAI, Anthropic, LangChain, or LangGraph inference path is implemented.
* **No Answer Synthesis or Automated Claim Verification:** SQL outputs and document chunks are presented separately.
* **No Dense/Vector or Hybrid Retrieval:** Document retrieval uses BM25 with metadata boosts.
* **No Arbitrary SQL Execution Endpoint:** Query compilation and database access are deliberately constrained.
* **Not Production-Hardened:** Authentication, authorization, and deployment security are not implemented.
* **Known Correctness Gaps:** Three executable questions in the 50-case evaluation still fail; synthetic benchmarks do not establish real-world performance.

---

## Project Status

**Working prototype — active development.** 

The current emphasis is on predictable query interpretation, transparent execution, measurable correctness, and safe local analytics rather than broad language-model capabilities.