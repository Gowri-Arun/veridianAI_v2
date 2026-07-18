# Week 6 Implementation Report

## Status

Week 6 status: complete.

The repository now has a deterministic SQL benchmark suite, validator, evaluator, report generator, reproducible environment checks, setup helpers, and generated JSON/CSV/Markdown evaluation outputs.

## Benchmark

- Gold file: `benchmarks/sql_gold.jsonl`
- Cases: 57
- Executable cases: 45
- Categories: `metric_lookup`, `grouped_metric`, `period_comparison`, `absolute_change`, `percentage_change`, `multiple_metrics`, `top_n`, `count_query`, `ambiguous`, `unsupported`, `adversarial`
- Difficulties: `easy`, `medium`, `hard`, `adversarial`

## Latest SQL Eval

- Cases evaluated: 57
- Passed: 57
- Failed: 0
- Overall case accuracy: 1.0000
- Outputs:
  - `experiments/results/sql_eval_results.json`
  - `experiments/results/sql_eval_results.csv`
  - `reports/sql_benchmark_report.md`

## Supported Metrics

`revenue`, `bookings`, `marketing_spend`, `churn`, `customer_count`, `support_tickets`, `pipeline`, `conversion_rate`, `product_usage`, `subscriptions`, `region_target`.

## Supported Dimensions

`quarter`, `region`, `segment`, `product`, `channel`, `industry`, `status`, `severity`.

## Supported Query Shapes

Single metric lookup, grouped metric, period comparison, absolute change, percentage change, multiple independent metrics, top-N grouped metric, and count query.

## Unsupported Query Shapes

Arbitrary joins, correlation analysis, forecasting, transaction-level requests, raw SQL requests, file reads, extension loading, mutation, and answer synthesis remain unsupported.

## Safety Controls

Compiled SQL must be a single `SELECT`, must use registered tables and columns, must parameterize user values, must pass forbidden keyword/function checks, and executes through a read-only DuckDB connection. Parameter values are also checked for SQL control text and mutation keywords.

## Retrieval Benchmark

Latest BM25 retrieval evaluation:

- Recall@3: 0.6500
- Recall@5: 0.7833
- Recall@10: 0.8533
- Hit Rate@3: 0.8800
- Hit Rate@5: 0.9200
- Hit Rate@10: 0.9200
- MRR: 0.6500

## Environment Notes

The sandbox `python` can resolve to MSYS Python without pip. Verified project commands were run with the project Python at `C:\Users\gowri\AppData\Local\Programs\Python\Python313\python.exe`. `scripts.check_environment` records the active executable, dependency imports, data paths, and output directories.

FastAPI/Streamlit dependency compatibility is pinned with `starlette>=0.40,<0.45` and `streamlit>=1.36,<1.50`.

## Verification Commands

- `python -m pytest`
- `python -m compileall app frontend scripts tests`
- `python -m scripts.validate_week2_data`
- `python -m scripts.run_retrieval_eval`
- `python -m scripts.validate_sql_benchmark`
- `python -m scripts.run_sql_eval`
- `python -m scripts.generate_sql_gold_results`
- `python -m scripts.inspect_duckdb_schema`
- Focused TestClient route checks for SQL and hybrid responses
- Focused SQL read-only and safety checks

## Known Limitations

The benchmark validates deterministic SQL behavior and result shape, not free-form text-to-SQL or narrative answer quality. Numeric gold materialization is intentionally not generated from the system planner; stable checks are row-count, column, comparison, and typed behavior checks.

Recommended Week 7 starting point: add a trusted independent numeric oracle for benchmark expected rows, then expand coverage for joins only if a registry-backed join policy is implemented first.
