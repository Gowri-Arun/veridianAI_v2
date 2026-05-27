# Failure Taxonomy

## 1. Retrieval failures
- **Failure:** Relevant documents are not retrieved.
- **Example:** A pricing memo about APAC objections is missing.
- **Why it happens:** Weak keyword match, poor chunking, or incomplete index.
- **How to detect:** Missing expected evidence in retrieved results.
- **Possible fix:** Improve indexing, metadata, and retrieval tuning.
- **Evaluation metric:** Recall@K

## 2. Semantic mapping failures
- **Failure:** User terms are mapped to the wrong business concept.
- **Example:** "pipeline" is treated as recognized revenue.
- **Why it happens:** Ambiguous terminology and weak schema mapping.
- **How to detect:** The generated interpretation conflicts with metric definitions.
- **Possible fix:** Add concept definitions and clarification rules.
- **Evaluation metric:** Metric mapping accuracy

## 3. Planning failures
- **Failure:** The wrong evidence path is selected.
- **Example:** The system chooses only SQL when documents are needed.
- **Why it happens:** Planner does not understand query complexity.
- **How to detect:** The plan omits required evidence sources.
- **Possible fix:** Add stronger routing logic and planner heuristics.
- **Evaluation metric:** Plan accuracy

## 4. SQL generation failures
- **Failure:** Generated SQL is syntactically or semantically wrong.
- **Example:** The query compares incorrect quarters.
- **Why it happens:** Incorrect schema or bad prompt selection.
- **How to detect:** SQL validation errors or wrong result shape.
- **Possible fix:** Add schema-aware SQL generation and validation.
- **Evaluation metric:** SQL execution accuracy

## 5. SQL execution failures
- **Failure:** Query runs but returns incorrect or empty results.
- **Example:** Wrong table name or invalid filter.
- **Why it happens:** Bugs in query construction or data mismatch.
- **How to detect:** Database errors or unexpected row counts.
- **Possible fix:** Add query validation and schema checks.
- **Evaluation metric:** SQL execution accuracy

## 6. Analysis failures
- **Failure:** The system misinterprets trends or comparisons.
- **Example:** Marketing spend increase is treated as the direct cause of revenue decline.
- **Why it happens:** Correlation is mistaken for causation.
- **How to detect:** Analysis contradicts domain expectations.
- **Possible fix:** Require evidence-based causal language and separate facts from hypotheses.
- **Evaluation metric:** Analysis correctness

## 7. Synthesis failures
- **Failure:** Final answer is unclear, incomplete, or incorrectly summarized.
- **Example:** The answer omits the source of churn increase.
- **Why it happens:** The model compresses evidence poorly.
- **How to detect:** Missing expected answer points.
- **Possible fix:** Add structured answer templates.
- **Evaluation metric:** Answer completeness

## 8. Citation failures
- **Failure:** Claims are made without evidence.
- **Example:** The answer cites a document that does not support the claim.
- **Why it happens:** Incomplete grounding logic.
- **How to detect:** Compare claims with retrieved evidence and SQL results.
- **Possible fix:** Enforce citation checks.
- **Evaluation metric:** Citation precision

## 9. Verification failures
- **Failure:** The system fails to check support for its own claims.
- **Example:** No verification step is run before response generation.
- **Why it happens:** Verification pipeline is missing or weak.
- **How to detect:** Missing verification artifacts in logs.
- **Possible fix:** Add deterministic verification checks.
- **Evaluation metric:** Faithfulness

## 10. Ambiguity handling failures
- **Failure:** Ambiguous questions are answered as if they were clear.
- **Example:** Asking about "sales" without clarifying the metric.
- **Why it happens:** The system overcommits to a single interpretation.
- **How to detect:** No clarification request or contradictory interpretation.
- **Possible fix:** Add ambiguity detection and clarification prompts.
- **Evaluation metric:** Ambiguity resolution rate

## 11. Unanswerable question failures
- **Failure:** The system invents an answer when the data does not support one.
- **Example:** Guessing which individual customer caused churn.
- **Why it happens:** The system assumes hidden data exists.
- **How to detect:** Missing evidence or unsupported entities.
- **Possible fix:** Return "unanswerable" with explanation.
- **Evaluation metric:** Unanswerable detection accuracy

## 12. Overconfidence failures
- **Failure:** The answer sounds certain despite weak evidence.
- **Example:** The system states a single cause when only a likely explanation is available.
- **Why it happens:** The answer lacks uncertainty language.
- **How to detect:** Overstated claims without confidence or evidence.
- **Possible fix:** Add confidence labels and uncertainty framing.
- **Evaluation metric:** Calibration / overconfidence rate
