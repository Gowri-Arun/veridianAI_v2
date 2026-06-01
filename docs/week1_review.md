# Week 1 Review

## What is Veridian AI?

Veridian AI is an evaluation-driven enterprise query engine for grounded analytics.

## Why is it evaluation-driven?

It is designed to measure retrieval quality, SQL correctness, grounding, faithfulness, and answer reliability.

## What are the main components?

- Intent understanding
- Semantic mapping
- Planner
- Retrieval
- SQL engine
- Analysis
- Synthesis
- Verification
- Evaluation logging

## What are the main failure modes?

- retrieval failures
- semantic mapping failures
- planning failures
- SQL generation failures
- SQL execution failures
- analysis failures
- synthesis failures
- citation failures
- verification failures
- ambiguity handling failures
- unanswerable question failures
- overconfidence failures

## What does the benchmark test?

The benchmark tests simple lookup, comparison, hybrid reasoning, ambiguity handling, contradiction detection, and unanswerable behavior.

## Why are user engagement metrics not the main metric?

User engagement does not measure correctness, grounding, or reliability.

## What is intentionally not built yet?

- LangGraph
- production-grade retrieval
- vector search
- LLM prompt orchestration
- full SQL generation pipeline
- fancy frontend UI
