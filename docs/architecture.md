# Architecture

## High-Level Flow

User Query
→ Intent Understanding
→ Semantic Mapping
→ Planner
→ Retrieval
→ SQL Engine
→ Analysis
→ Synthesis
→ Verification
→ Final Answer
→ Evaluation Logging

## Component Responsibilities

### 1. Intent Understanding

Identifies what the user is asking.

Examples:
- simple lookup
- metric comparison
- trend analysis
- root-cause analysis
- ambiguous question
- unanswerable question

### 2. Semantic Mapping

Maps user terms to business definitions.

Examples:
- "sales" may mean revenue, bookings, or pipeline
- "large customers" may mean enterprise segment
- "last quarter" must be converted to a specific quarter

### 3. Planner

Decides what evidence is needed.

Examples:
- SQL query needed
- document retrieval needed
- both SQL and documents needed
- clarification needed

### 4. Retrieval

Finds relevant unstructured documents.

Examples:
- pricing memos
- support reports
- quarterly business reviews
- internal notes

### 5. SQL Engine

Queries structured data.

Examples:
- revenue by quarter
- churn by region
- marketing spend by segment

### 6. Analysis

Compares numbers and identifies patterns.

Examples:
- revenue decreased
- churn increased
- marketing spend increased
- support escalations increased

### 7. Synthesis

Combines evidence into a clear answer.

### 8. Verification

Checks whether the final answer is supported by retrieved evidence and SQL results.

### 9. Evaluation Logging

Stores query, plan, retrieved docs, SQL, answer, metrics, and failure modes.

## Deterministic vs LLM-Based Components

### Deterministic Components

These should be handled by code whenever possible:
- SQL execution
- SQL validation
- metric registry lookup
- schema lookup
- retrieval metric calculation
- citation checking
- numeric claim checking
- latency tracking
- cost tracking

### LLM-Based Components

These may require language understanding:
- intent parsing
- flexible query planning
- ambiguous query interpretation
- answer synthesis
- claim extraction
- semantic evaluation

## Why This Separation Matters

The system should not use an LLM for everything.

If a task can be checked deterministically, it should be checked deterministically.

This improves reliability, debuggability, and trust.
