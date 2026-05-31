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
