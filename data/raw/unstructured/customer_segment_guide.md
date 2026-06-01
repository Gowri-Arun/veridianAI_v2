---
doc_id: customer_segment_guide
title: Customer Segment Operational Guide
doc_type: reference_document
quarter: All
region: Global
segment: All
related_metrics:
  - recognized_revenue
  - churn_rate
  - usage_score
source: synthetic_internal_reference
---

# Customer Segment Operational Guide

This guide defines NovaCloud Analytics' customer segments and outlines how each segment behaves operationally.

## Segment Characteristics

### Enterprise
High-value contracts with low volume. Enterprise accounts require custom onboarding and dedicated customer success management. They exhibit high product usage scores but are sensitive to technical stability issues.

### Mid-Market
Moderate contract value with steady growth. Mid-Market accounts are stable but highly sensitive to pricing updates and packaging changes.

### SMB
High-volume, self-serve contracts. SMB accounts are highly sensitive to support response times. When support response times exceed 24 hours, SMB accounts experience rapid silent churn.

## Related Documents
- [regional_taxonomy.md](regional_taxonomy.md) — how segments map to regions
- [known_metric_confusions.md](known_metric_confusions.md) — traps in segment-level metric analysis
