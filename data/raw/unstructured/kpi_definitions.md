---
doc_id: kpi_definitions
title: KPI Definitions Guide
doc_type: reference_document
quarter: All
region: Global
segment: All
related_metrics:
  - recognized_revenue
  - bookings
  - pipeline_value
  - gross_margin
  - churn_rate
  - retention_rate
  - marketing_spend
  - conversion_rate
  - support_escalations
  - usage_score
  - ARR
source: synthetic_internal_reference
---

# KPI Definitions Guide

This reference document defines the standard Key Performance Indicators (KPIs) utilized across NovaCloud Analytics. Consistency in metric reporting is essential for accurate business intelligence.

## Financial Metrics

### Recognized Revenue
Recognized revenue is the value of services actually delivered to the customer in a given quarter, under ASC 606 standards. For multi-quarter subscriptions, bookings are recognized on a straight-line basis over the contract term.

### Bookings
Bookings represent the total contractual value of signed commitments. It measures sales velocity but does not translate directly to immediate revenue recognition or cash flow.

### Annual Recurring Revenue (ARR)
The annualized run-rate of recurring subscription software fees. ARR is calculated as: `ARR = MRR * 12`. It excludes one-time services or setup fees.

### Gross Margin
Gross Margin measures the profitability of software delivery, calculated as: `(Recognized Revenue - Cost of Goods Sold) / Recognized Revenue`. COGS includes hosting costs and customer support personnel.

## Operational & Sales Funnel Metrics

### Pipeline Value
The estimated aggregate contract value of active sales opportunities in the funnel. Pipeline represents potential future sales, typically weighted by win probability.

### Conversion Rate
The ratio of closed-won opportunities to the total number of qualified opportunities in the pipeline during a given period.

### Churn Rate & Retention Rate
- Churn Rate is the percentage of ARR or customer logos lost in a period.
- Retention Rate (Net Retention Rate or NRR) represents retained ARR including expansions, calculated as: `(Starting ARR + Expansion - Churn) / Starting ARR`.

## Product & Support Metrics

### Support Escalations
Support tickets of high severity that cannot be resolved by primary agents and are escalated to engineering or product teams.

### Usage Score
An indexed metric (0 to 100) that calculates account health based on weekly active users (WAU) and the variety of advanced features accessed.
