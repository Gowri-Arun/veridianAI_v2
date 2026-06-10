# BM25 Retrieval Baseline Report

**Generated:** 2026-06-10 14:45:31

## Summary

- **Benchmark size:** 25 retrieval gold queries
- **Retriever:** BM25 (deterministic, built-in)
- **Top-K evaluated:** 10

## Metrics

| Metric | Value |
|--------|-------|
| Average Recall@3 | 0.6500 |
| Average Recall@5 | 0.7833 |
| Average Recall@10 | 0.8533 |
| Hit Rate@3 | 0.8800 |
| Hit Rate@5 | 0.9200 |
| Hit Rate@10 | 0.9200 |
| MRR | 0.6500 |

## Results Table

| ID | Query | Type | Difficulty | Recall@3 | Recall@5 | Recall@10 | Hit@3 | Hit@5 | Hit@10 | RR | Failure |
|----|-------|------|------------|----------|----------|-----------|-------|-------|--------|----|---------|
| rg_001 | What is the difference between recognized revenue  | simple_document | easy | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | no_failure |
| rg_002 | What does churn rate mean in this analytics system | simple_document | easy | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | no_failure |
| rg_003 | Why should pipeline value not be treated as recogn | simple_document | easy | 0.5000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | no_failure |
| rg_004 | What happened to EMEA pipeline in Q4 2025 and why  | hybrid_sql_document | hard | 0.7500 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | no_failure |
| rg_005 | What evidence suggests pricing changes affected AP | hybrid_sql_document | hard | 0.5000 | 0.5000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | generic_doc_ranked_too_high |
| rg_006 | How did support escalations relate to Enterprise c | hybrid_sql_document | hard | 0.5000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.3333 | no_failure |
| rg_007 | What was the FlowOps v2.0 Q4 release side effect f | hybrid_sql_document | hard | 0.7500 | 0.7500 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | generic_doc_ranked_too_high |
| rg_008 | How can product usage decline warn of future churn | hybrid_sql_document | medium | 0.3333 | 0.3333 | 0.3333 | 1.0000 | 1.0000 | 1.0000 | 0.3333 | no_failure |
| rg_009 | Which regions missed revenue or margin targets in  | hybrid_sql_document | medium | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | weak_query_terms |
| rg_010 | What likely factors weakened APAC Enterprise perfo | root_cause_analysis | hard | 0.5000 | 0.7500 | 0.7500 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | no_failure |
| rg_011 | What drove the SMB churn spike after support slowe | hybrid_sql_document | hard | 0.2500 | 0.5000 | 0.7500 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | generic_doc_ranked_too_high |
| rg_012 | Why did APAC Enterprise revenue decline while mark | root_cause_analysis | hard | 0.5000 | 0.5000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | generic_doc_ranked_too_high |
| rg_013 | Define the key performance indicators used in Nova | simple_document | easy | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | no_failure |
| rg_014 | What are the common metric confusions users should | simple_document | easy | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | no_failure |
| rg_015 | What happened to APAC Enterprise recognized revenu | hybrid_sql_document | medium | 0.5000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | no_failure |
| rg_016 | How does the EMEA sales cycle length affect pipeli | hybrid_sql_document | medium | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | no_failure |
| rg_017 | What technical failures occurred with the FlowOps  | simple_document | medium | 0.5000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | no_failure |
| rg_018 | What customer segments are defined and how do they | simple_document | easy | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | no_failure |
| rg_019 | What is the relationship between marketing spend a | hybrid_sql_document | medium | 0.6667 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | no_failure |
| rg_020 | Summarize the Q4 2025 business review across all r | simple_document | medium | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | missing_expected_doc |
| rg_021 | What retention concerns exist for Enterprise custo | simple_document | medium | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | no_failure |
| rg_022 | How did SMB churn trends evolve in Q4 2025? | hybrid_sql_document | medium | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | no_failure |
| rg_023 | What were the Q1, Q2, Q3, and Q4 2025 business rev | simple_document | easy | 0.0000 | 0.2500 | 0.5000 | 0.0000 | 1.0000 | 1.0000 | 0.2500 | generic_doc_ranked_too_high |
| rg_024 | What does the support escalation report say about  | simple_document | easy | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.3333 | no_failure |
| rg_025 | How do regional segments map across the organizati | simple_document | easy | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | no_failure |

## Failed Cases

**7 queries** with retrieval failures:

- **rg_005**: What evidence suggests pricing changes affected APAC Enterprise customers?
  - Failure: `generic_doc_ranked_too_high`
  - Expected: ['pricing_change_memo', 'q4_apac_revenue_report']
  - Retrieved (top 10, deduped): ['customer_segment_guide', 'pricing_change_memo', 'known_metric_confusions', 'q3_business_review', 'q2_business_review', 'q4_apac_revenue_report']
  - Recall@10: 1.0000

- **rg_007**: What was the FlowOps v2.0 Q4 release side effect for Enterprise customers?
  - Failure: `generic_doc_ranked_too_high`
  - Expected: ['flowops_release_incident', 'product_release_notes', 'enterprise_retention_notes', 'q4_business_review']
  - Retrieved (top 10, deduped): ['q4_business_review', 'product_release_notes', 'flowops_release_incident', 'support_escalation_report', 'q4_apac_revenue_report', 'enterprise_retention_notes']
  - Recall@10: 1.0000

- **rg_009**: Which regions missed revenue or margin targets in Q4 2025?
  - Failure: `weak_query_terms`
  - Expected: ['regional_taxonomy', 'q4_business_review']
  - Retrieved (top 10, deduped): ['q1_business_review', 'q4_apac_revenue_report', 'emea_pipeline_review', 'kpi_definitions', 'product_release_notes', 'sales_cycle_review', 'schema_definitions', 'flowops_release_incident']
  - Recall@10: 0.0000

- **rg_011**: What drove the SMB churn spike after support slowed down?
  - Failure: `generic_doc_ranked_too_high`
  - Expected: ['smb_churn_review', 'customer_success_notes', 'support_escalation_report', 'q4_business_review']
  - Retrieved (top 10, deduped): ['emea_pipeline_review', 'smb_churn_review', 'known_metric_confusions', 'support_escalation_report', 'q3_business_review', 'customer_success_notes', 'customer_segment_guide']
  - Recall@10: 0.7500

- **rg_012**: Why did APAC Enterprise revenue decline while marketing spend increased?
  - Failure: `generic_doc_ranked_too_high`
  - Expected: ['q4_apac_revenue_report', 'pricing_change_memo', 'support_escalation_report', 'marketing_campaign_memo']
  - Retrieved (top 10, deduped): ['marketing_campaign_memo', 'known_metric_confusions', 'q4_apac_revenue_report', 'kpi_definitions', 'q4_business_review', 'support_escalation_report', 'pricing_change_memo']
  - Recall@10: 1.0000

- **rg_020**: Summarize the Q4 2025 business review across all regions.
  - Failure: `missing_expected_doc`
  - Expected: ['q4_business_review']
  - Retrieved (top 10, deduped): ['smb_churn_review', 'regional_taxonomy', 'q1_business_review', 'sales_cycle_review', 'support_escalation_report', 'emea_pipeline_review', 'kpi_definitions']
  - Recall@10: 0.0000

- **rg_023**: What were the Q1, Q2, Q3, and Q4 2025 business reviews?
  - Failure: `generic_doc_ranked_too_high`
  - Expected: ['q1_business_review', 'q2_business_review', 'q3_business_review', 'q4_business_review']
  - Retrieved (top 10, deduped): ['enterprise_retention_notes', 'pricing_change_memo', 'customer_success_notes', 'q1_business_review', 'flowops_release_incident', 'sales_cycle_review', 'emea_pipeline_review', 'q3_business_review', 'smb_churn_review']
  - Recall@10: 0.5000

## Observations

- BM25 provides deterministic, explainable retrieval without external dependencies.
- The retriever handles definition queries well when query terms overlap with document text.
- Multi-document queries requiring synthesis across several documents are challenging for BM25 alone.
- Failure cases typically involve queries where expected documents do not share significant term overlap with the query.

## Known Limitations

- BM25 is purely lexical and cannot capture semantic similarity.
- Synonyms and business jargon that differ from document terminology cause misses.
- No query expansion, no relevance feedback, no learning-to-rank.
- Only 20 documents (120 chunks) in the corpus; results may not generalize to larger corpora.
- Gold labels are synthetic and may not reflect real-world retrieval difficulty.

## Week 5 Recommendation

Implement vector retrieval (embedding-based) and compare against the BM25 baseline. If vector retrieval improves Recall@10 and MRR meaningfully, implement hybrid retrieval that combines BM25 and vector scores. Evaluate reranking as a final precision layer.
