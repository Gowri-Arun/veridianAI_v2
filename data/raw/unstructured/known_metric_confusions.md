---
doc_id: known_metric_confusions
title: Known Metric Confusions and Traps
doc_type: reference_document
quarter: All
region: Global
segment: All
related_metrics:
  - recognized_revenue
  - bookings
  - pipeline_value
  - churn_rate
  - support_escalations
source: synthetic_internal_reference
---

# Known Metric Confusions and Traps

This guide documents common metric confusions and analytical traps to prevent reporting errors in Veridian AI.

## Financial Misunderstandings

### Recognized Revenue vs. Bookings
Bookings represent signed contract value, while recognized revenue represents services actually delivered under ASC 606. A $120,000 annual booking recognizes only $10,000 of revenue per month.

### Pipeline Value is Speculative
Pipeline is the estimated value of active opportunities. It is not guaranteed revenue. EMEA's Q4 pipeline appeared inflated due to speculative deals that failed to convert.

## Operational Misunderstandings

### Churn vs. Support Tickets
Support ticket volume is a leading indicator of churn, but not every ticket leads to churn. Some clients churn silently due to low platform usage without filing tickets.

### ARR vs. Recognized Revenue
ARR represents the annualized run-rate of active subscriptions. Historical recognized revenue can include one-time setup fees and service refunds, resulting in variance between the two metrics.
