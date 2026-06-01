# NovaCloud Analytics — Enterprise Data Design

## Company Overview
NovaCloud Analytics is a B2B SaaS analytics platform headquartered in San Francisco, with regional offices in London, Singapore, and São Paulo. The company provides a suite of data products that help organizations ingest, model, visualize, and act on their operational data in real time. NovaCloud serves over 2,000 customers across four continents and operates on a subscription-based pricing model with tiered service levels.

## Products

| Product     | Description                                                                 | Primary Users         |
|-------------|-----------------------------------------------------------------------------|------------------------|
| **InsightOS** | Core BI and visualization platform. Dashboards, ad-hoc queries, report scheduling. | Analysts, Executives   |
| **MetricHub** | Semantic metric store and governance layer. Single source of truth for KPIs. | Data Engineers, Analysts |
| **FlowOps**   | Data orchestration and ETL engine. Pipeline automation, monitoring, alerting. | Data Engineers, Ops    |

## Regions

| Region       | Headquarters  | Primary Timezone | Maturity   |
|--------------|---------------|------------------|------------|
| **APAC**     | Singapore     | SGT (UTC+8)      | Growth     |
| **EMEA**     | London        | GMT/BST (UTC+0/+1) | Mature    |
| **North America (NA)** | San Francisco | PT (UTC-8/-7) | Core      |
| **LATAM**    | São Paulo     | BRT (UTC-3)      | Emerging   |

## Customer Segments

| Segment       | Customer Count Share | Average Deal Size | Sales Cycle | Support Model        |
|---------------|----------------------|-------------------|-------------|----------------------|
| **SMB**       | ~60%                 | $5K–$20K ARR      | 1–4 weeks   | Self-serve + Chat    |
| **Mid-Market**| ~25%                 | $20K–$100K ARR    | 4–12 weeks  | Shared CSM           |
| **Enterprise**| ~15%                 | $100K–$1M+ ARR    | 12–24 weeks | Dedicated CSM + TAM  |

## Time Periods
All structured data covers four fiscal quarters:

- **Q1_2025** (Jan–Mar)
- **Q2_2025** (Apr–Jun)
- **Q3_2025** (Jul–Sep)
- **Q4_2025** (Oct–Dec)

## Core Business Metrics

| Metric                | Definition                                                                 | Data Source              |
|-----------------------|----------------------------------------------------------------------------|--------------------------|
| Recognized Revenue    | Revenue earned under ASC 606 from delivered subscriptions/services         | `revenue` table          |
| Bookings              | Signed contract value (TCV/ACV) committed by customers                     | `subscriptions` / `sales_pipeline` |
| Pipeline              | Aggregate value of open sales opportunities at any stage                   | `sales_pipeline` table   |
| ARR                   | Annualized recurring revenue from active subscriptions                     | `subscriptions` table    |
| Churn Rate            | % of customers or ARR lost in a period                                      | `churn` table            |
| Retention Rate        | % of customers or ARR retained (gross and net)                             | `churn` + `subscriptions`|
| Marketing Spend       | Dollars spent on demand generation, events, paid search, content           | `marketing_spend` table  |
| Conversion Rate       | % of pipeline deals that close won                                        | `sales_pipeline` table   |
| Support Escalations   | Tickets requiring senior or engineering intervention                       | `support_tickets` table  |
| Product Usage         | Active users, feature adoption, API error rates                            | `product_usage` table    |
| Gross Margin          | (Revenue – COGS) / Revenue                                                | Derived from financials  |

## Structured Tables

| Table               | Grain                         | Key Entities                          |
|---------------------|-------------------------------|----------------------------------------|
| `revenue`           | One row per customer per product per quarter | customer_id, product_id, quarter       |
| `customers`         | One row per customer          | customer_id, segment, region, status   |
| `marketing_spend`   | One row per region-segment-channel per quarter | quarter, region, segment, channel      |
| `churn`             | One row per churn event       | customer_id, churn_quarter, reason     |
| `support_tickets`   | One row per support ticket    | ticket_id, customer_id, severity       |
| `product_usage`     | One row per customer per product per quarter | customer_id, product_id, quarter       |
| `sales_pipeline`    | One row per opportunity       | opportunity_id, region, segment, stage |
| `subscriptions`     | One row per subscription      | subscription_id, customer_id, arr      |
| `region_targets`    | One row per region-segment per quarter | quarter, region, segment, target_arr |

### Table Relationships

```
customers ──< subscriptions
customers ──< revenue
customers ──< churn
customers ──< support_tickets
customers ──< product_usage
region_targets ─── (no direct FK; filtered by region + segment)
sales_pipeline ─── (references customer_name, no FK to customers)
marketing_spend ── (no direct FK; filtered by region + segment)
```

## Unstructured Documents

The following unstructured artifacts complement the structured tables and contain narrative context for the hidden business stories:

| Document Type                 | Content Description                                          | Narrative Relevance          |
|-------------------------------|--------------------------------------------------------------|------------------------------|
| QBR Presentations             | Regional quarterly business reviews with commentary           | All narratives               |
| Support Escalation Logs       | Post-mortem write-ups for critical outages                   | Narratives 1, 3, 4           |
| Product Release Notes         | Changelogs for FlowOps v2.0 and other releases               | Narrative 4                  |
| Internal Slack / Email Threads| Sales and engineering communications about deals and bugs    | Narratives 2, 4              |
| Customer Exit Surveys         | Churn reason collection from departing customers             | Narratives 1, 3              |
| Compliance Memoranda          | Legal/regulatory updates affecting sales cycles              | Narrative 2                  |

## Hidden Narratives Overview

Four business storylines are woven into the dataset. Each requires joining multiple tables and reading unstructured documents to fully diagnose:

1. **APAC Enterprise Revenue Drop** — Q4_2025 revenue decline despite increased marketing spend, driven by pricing-changes, onboarding failures, and support gaps.
2. **EMEA Pipeline Illusion** — Q4_2025 pipeline surge masks declining conversion rates and lengthening sales cycles.
3. **SMB Churn After Support Slowdown** — Q3/Q4_2025 SMB churn spike follows support reallocation away from SMB and declining product usage.
4. **FlowOps Release Side Effect** — Q4_2025 FlowOps v2.0 release causes instability, support escalations, and Enterprise usage drop.

## Design Principles

1. **Internal Consistency**: Every quantitative figure in structured tables must cross-reference the narratives. If APAC Enterprise revenue drops in Q4_2025, the `revenue`, `churn`, `support_tickets`, and `marketing_spend` tables must collectively reflect that reality without contradiction.

2. **Traceability**: Each narrative has a breadcrumb trail through `region`, `segment`, `product_id`, and `quarter` keys. An analyst should be able to start from any table and recursively join to discover the full story.

3. **Realistic SaaS Dynamics**: Data simulates real-world patterns — seasonality, support-to-churn lag, delayed revenue recognition, sales pipeline inflation, and product-release side effects. No "perfect" linear trends.

4. **Multi-Table Diagnosis**: No single table tells a complete story. Every narrative requires at least 3 structured tables plus at least one unstructured document to diagnose correctly.

5. **Leading vs. Lagging Indicators**: Metrics are arranged so that leading indicators (product usage, support response time) appear in earlier quarters than the lagging outcomes (churn, revenue drop). This enables predictive analysis workflows.

6. **Metric Ambiguity**: Deliberately confusable metrics (e.g., bookings vs. recognized revenue, pipeline vs. guaranteed revenue) are included to test whether the system correctly disambiguates terms.

7. **Nulls and Edge Cases**: Foreign keys may not always resolve (e.g., pipeline opportunities referencing prospects not yet in `customers`). This mirrors real data quality challenges.

8. **No Single Source of Truth Violations**: When metrics disagree (e.g., marketing spend up but revenue down), there is always a causal explanation in the unstructured documents — the data never contradicts itself without reason.
