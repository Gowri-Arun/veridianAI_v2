# Benchmark Schema

## Purpose of benchmark

The benchmark is designed to evaluate whether the system can understand ambiguous business questions, ground answers in evidence, and avoid unsupported claims.

## Query types

- simple_document
- simple_sql
- metric_lookup
- comparison
- trend_analysis
- hybrid_sql_document
- root_cause_analysis
- ambiguous
- unanswerable
- contradiction
- adversarial

## JSONL schema

Each JSONL line should contain the following fields:

- id: unique benchmark identifier
- question: natural language question
- query_type: one of the supported query types
- difficulty: easy, medium, or hard
- expected_intent: expected system intent
- expected_metrics: metrics that should be referenced
- expected_dimensions: dimensions such as region, quarter, segment
- expected_filters: filters such as APAC, Q4 2025
- expected_tables: structured tables that may be needed
- expected_docs: relevant documents or document categories
- expected_answer_points: key facts that should appear in the answer
- known_traps: expected failure modes or traps
- evaluation_targets: metrics or checks to apply

## Field explanations

- **id**: unique identifier for the benchmark item
- **question**: the user question
- **query_type**: the category of the question
- **difficulty**: the expected difficulty level
- **expected_intent**: the intended route for the system
- **expected_metrics**: metrics that need to be surfaced
- **expected_dimensions**: dimensions such as geography, customer segment, or time
- **expected_filters**: conditions that should be applied
- **expected_tables**: likely structured tables required
- **expected_docs**: likely documents or evidence sources
- **expected_answer_points**: facts that the answer should include
- **known_traps**: traps that evaluate hallucination or ambiguity handling
- **evaluation_targets**: what the evaluation should measure

## Evaluation targets

The benchmark should test:
- retrieval correctness
- SQL correctness
- semantic interpretation
- grounding and faithfulness
- ambiguity handling
- unanswerable detection
- contradiction handling
- citation quality
- answer completeness
- overconfidence control
