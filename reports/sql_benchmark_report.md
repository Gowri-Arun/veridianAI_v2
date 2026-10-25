# SQL Benchmark Report

Generated: 2026-07-18T02:56:37.870891+00:00
Repository commit: 1b44b54
Benchmark cases: 57

## Distribution

Category distribution: `{'metric_lookup': 8, 'grouped_metric': 7, 'period_comparison': 7, 'absolute_change': 5, 'percentage_change': 5, 'multiple_metrics': 5, 'top_n': 4, 'count_query': 4, 'ambiguous': 3, 'unsupported': 3, 'adversarial': 6}`
Difficulty distribution: `{'easy': 13, 'medium': 26, 'hard': 12, 'adversarial': 6}`

## Metrics

| Metric | Value |
|---|---:|
| semantic_parse_accuracy | 1.0000 |
| metric_selection_accuracy | 1.0000 |
| dimension_selection_accuracy | 1.0000 |
| filter_accuracy | 1.0000 |
| period_accuracy | 1.0000 |
| query_shape_accuracy | 1.0000 |
| table_selection_accuracy | 1.0000 |
| column_selection_accuracy | 1.0000 |
| aggregation_accuracy | 1.0000 |
| grouping_accuracy | 1.0000 |
| execution_success_rate | 1.0000 |
| result_accuracy | 1.0000 |
| comparison_accuracy | 1.0000 |
| clarification_accuracy | 1.0000 |
| unsupported_rejection_accuracy | 1.0000 |
| adversarial_block_rate | 1.0000 |
| overall_case_accuracy | 1.0000 |

## Failure Categories

`{}`

## Failed Cases

No failed cases.

## Known Limitations

- The benchmark evaluates deterministic SQL semantics, not answer synthesis.
- Expected numeric rows are intentionally bounded to stable row-count/column/comparison checks unless materialized by a trusted reference path.
- No LLM-as-judge is used.