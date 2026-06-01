---
doc_id: schema_definitions
title: Database Schema Definitions
doc_type: reference_document
quarter: All
region: Global
segment: All
related_metrics:
  - recognized_revenue
  - bookings
  - churn_rate
  - usage_score
source: synthetic_internal_reference
---

# Database Schema Definitions

This document details the schema of NovaCloud Analytics' central reporting tables, mapping operational data to corporate business intelligence warehouses.

## Relational Tables

### 1. revenue
Purpose: Tracks historical recognized revenue, bookings, and pipeline values.
- `quarter` (VARCHAR): Time period key.
- `region` (VARCHAR): Regional identifier.
- `segment` (VARCHAR): Segment grouping (SMB, Mid-Market, Enterprise).
- `product` (VARCHAR): Product catalog line.
- `recognized_revenue` (DECIMAL): Earned revenue under ASC 606.
- `bookings` (DECIMAL): Legally signed contracts.
- `pipeline_value` (DECIMAL): Estimated value of active opportunities.
- `gross_margin` (DECIMAL): Product direct margin.

### 2. customers
Purpose: Customer core registry.
- `customer_id` (VARCHAR): Unique customer primary key.
- `customer_name` (VARCHAR): Account name.
- `region` (VARCHAR): Region location.
- `segment` (VARCHAR): Client segment.
- `industry` (VARCHAR): Industry sector.
- `signup_quarter` (VARCHAR): Quarter account signed up.
- `status` (VARCHAR): Active or Churned.

### 3. subscriptions
Purpose: Active recurring subscription contracts.
- `subscription_id` (VARCHAR): Subscription primary key.
- `customer_id` (VARCHAR): Customer link.
- `product` (VARCHAR): Product catalog line.
- `plan_type` (VARCHAR): Plan type tier.
- `start_quarter` (VARCHAR): Active start quarter.
- `renewal_quarter` (VARCHAR): Expected renewal target.
- `arr` (DECIMAL): Annual Recurring Revenue run-rate.
- `status` (VARCHAR): Active or Cancelled.

### 4. support_tickets
Purpose: Support ticketing queue logs.
- `ticket_id` (VARCHAR): Ticket primary key.
- `customer_id` (VARCHAR): Customer link.
- `quarter` (VARCHAR): Quarter logged.
- `region` (VARCHAR): Region location.
- `segment` (VARCHAR): Client segment.
- `product` (VARCHAR): Product line.
- `issue_type` (VARCHAR): Categorized issue description.
- `severity` (VARCHAR): Low, Medium, High, Critical.
- `escalated` (BOOLEAN): Support escalation flag.
- `response_time_hours` (DECIMAL): First response duration.
- `resolution_time_hours` (DECIMAL): Close-out duration.

### 5. marketing_spend
Purpose: Tracks marketing budget allocation by region, channel, and quarter.
- `quarter` (VARCHAR): Time period key.
- `region` (VARCHAR): Target region.
- `channel` (VARCHAR): Marketing channel (Events, Paid Search, Content).
- `spend` (DECIMAL): Budget spent in USD.
- `campaign_name` (VARCHAR): Internal campaign identifier.
- `leads_generated` (INTEGER): Number of leads attributed to the campaign.

### 6. churn
Purpose: Logs contract cancellation events and churn rates by region and segment.
- `quarter` (VARCHAR): Churn event quarter.
- `region` (VARCHAR): Customer region.
- `segment` (VARCHAR): Customer segment.
- `churn_rate` (DECIMAL): Percentage of customers lost.
- `churned_customers` (INTEGER): Count of customers lost.
- `starting_customers` (INTEGER): Customer count at quarter start.
- `retention_rate` (DECIMAL): Percentage retained (1 - churn_rate).

### 7. product_usage
Purpose: Monitors product adoption, engagement depth, and account health.
- `quarter` (VARCHAR): Time period key.
- `region` (VARCHAR): Customer region.
- `segment` (VARCHAR): Customer segment.
- `product` (VARCHAR): Product catalog line.
- `active_users` (INTEGER): Monthly active user count.
- `usage_score` (DECIMAL): Account health index (0-100).
- `feature_adoption_rate` (DECIMAL): Fraction of features actively used.
- `avg_sessions_per_account` (DECIMAL): Average login sessions per account.

### 8. sales_pipeline
Purpose: Tracks sales opportunities through the deal funnel.
- `quarter` (VARCHAR): Quarter of opportunity record.
- `region` (VARCHAR): Target region.
- `segment` (VARCHAR): Target segment.
- `pipeline_value` (DECIMAL): Estimated total deal value.
- `opportunities_created` (INTEGER): Count of new opportunities.
- `win_rate` (DECIMAL): Fraction of deals that close won.
- `conversion_rate` (DECIMAL): Pipeline-to-closed-won conversion fraction.
- `avg_sales_cycle_days` (INTEGER): Average days from creation to close.

### 9. region_targets
Purpose: Sets quarterly ARR and revenue benchmarks per region.
- `quarter` (VARCHAR): Target period.
- `region` (VARCHAR): Target region.
- `revenue_target` (DECIMAL): Expected recognized revenue in USD.
- `pipeline_target` (DECIMAL): Expected pipeline value in USD.
- `churn_target` (DECIMAL): Maximum acceptable churn rate.
- `gross_margin_target` (DECIMAL): Minimum acceptable gross margin.

## Related Documents
- [kpi_definitions.md](kpi_definitions.md) — definitions of each metric stored in these tables
- [known_metric_confusions.md](known_metric_confusions.md) — common misinterpretations of table-level data
