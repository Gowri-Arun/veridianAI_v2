import os

def create_unstructured_docs():
    os.makedirs('data/raw/unstructured', exist_ok=True)
    
    docs = {}
    
    # 1. kpi_definitions.md
    docs['kpi_definitions'] = """---
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
"""

    # 2. schema_definitions.md
    docs['schema_definitions'] = """---
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
"""

    # 3. regional_taxonomy.md
    docs['regional_taxonomy'] = """---
doc_id: regional_taxonomy
title: Regional Taxonomy and Context
doc_type: reference_document
quarter: All
region: Global
segment: All
related_metrics:
  - recognized_revenue
  - marketing_spend
source: synthetic_internal_reference
---

# Regional Taxonomy and Context

NovaCloud Analytics operates across four distinct geographic regions. Each region operates under local business climates, presenting unique opportunities and structural operational constraints.

## Regional Profiles

### North America (NA)
Our largest and most mature market. Enterprise accounts in North America exhibit high contract values (ARR), steady feature adoption rates, and access standard round-the-clock support teams.

### EMEA (Europe, Middle East, and Africa)
A high-growth market characterized by rigid compliance requirements (GDPR, security reviews). Sales cycles in EMEA are historically longer due to these extensive compliance checkpoints.

### APAC (Asia-Pacific)
APAC is an emerging market presenting high potential. Historically, APAC has suffered from support coverage gaps due to time zone differences, creating customer friction during major releases.

### LATAM (Latin America)
A highly segment-focused market where Mid-Market accounts drive the majority of regional bookings. Operations are highly cost-sensitive, requiring efficient support SLA management.
"""

    # 4. q1_business_review.md
    docs['q1_business_review'] = """---
doc_id: q1_business_review
title: Q1 Business Review Report
doc_type: quarterly_review
quarter: Q1_2025
region: Global
segment: All
related_metrics:
  - recognized_revenue
  - bookings
  - churn_rate
  - support_escalations
source: synthetic_internal_report
---

# Q1 Business Review Report

This review summarizes corporate performance for the first quarter of fiscal year 2025. Q1 established a stable baseline with all core products showing healthy expansion metrics.

## Executive Summary
All key regions met or exceeded their initial recognized revenue targets. InsightOS remains the principal growth driver, while FlowOps ingestion systems processed record pipeline volumes.

## Metrics Dashboard
- Total Recognized Revenue: Met baseline target of $1.73M.
- Overall Gross Margin: Remained high at 79.2% average.
- Global Churn Rate: Solid at 4.2% across all segments, well within target thresholds.
- Support Ticket SLA Compliance: 94.6% resolved within standard targets.

## Regional Operational Highlights
North America and EMEA led bookings growth. Support escalations remained low, with an average initial response time of 2.4 hours globally. There are no major technical disruptions to report.
"""

    # 5. q2_business_review.md
    docs['q2_business_review'] = """---
doc_id: q2_business_review
title: Q2 Business Review Report
doc_type: quarterly_review
quarter: Q2_2025
region: Global
segment: All
related_metrics:
  - recognized_revenue
  - churn_rate
  - support_escalations
source: synthetic_internal_report
---

# Q2 Business Review Report

The second quarter of 2025 indicated continued high-level performance, though early signs of market friction emerged in specific segments.

## Segment Performance Trends
While the Enterprise segment grew steadily, the SMB segment experienced slight pressure. Churn in the SMB tier began rising toward the upper limit of acceptable thresholds.

## Operational & Support Alert
A reassignment of support specialists to Enterprise dedicated queues has increased general queue wait times. SMB customers are experiencing initial support response delays, with average response times increasing to 8.2 hours.

## Strategic Outlook
We are monitoring customer sensitivity to new pricing models being prepared for Q3. Regional heads are advised to ensure customer success teams maintain touchpoints with SMB customers to prevent silent churn.
"""

    # 6. q3_business_review.md
    docs['q3_business_review'] = """---
doc_id: q3_business_review
title: Q3 Business Review Report
doc_type: quarterly_review
quarter: Q3_2025
region: Global
segment: All
related_metrics:
  - recognized_revenue
  - churn_rate
  - support_escalations
  - usage_score
source: synthetic_internal_report
---

# Q3 Business Review Report

Q3 2025 demonstrated solid enterprise growth but highlighted severe operational constraints in our SMB self-serve tier.

## The SMB Support Friction
Following resource reallocations, SMB support queues have suffered significant latency. Average support response times rose past 24 hours. Consequently, SMB churn rates jumped to 14.0% in Q3.

## Product Adoption Warnings
Usage tracking indicates a steady drop in SMB usage scores. Decreasing feature adoption rates are acting as a leading indicator of contract cancellations.

## APAC Enterprise Friction
Our APAC teams report customer friction regarding pricing updates introduced this quarter. Several enterprise accounts expressed strong objections to the forced subscription migration, indicating contract renewal risks.
"""

    # 7. q4_business_review.md
    docs['q4_business_review'] = """---
doc_id: q4_business_review
title: Q4 Business Review Report
doc_type: quarterly_review
quarter: Q4_2025
region: Global
segment: All
related_metrics:
  - recognized_revenue
  - pipeline_value
  - churn_rate
  - support_escalations
source: synthetic_internal_report
---

# Q4 Business Review Report

Fourth-quarter performance was heavily impacted by three distinct structural issues despite record marketing spend.

## 1. APAC Enterprise Revenue Drop
Recognized revenue in the APAC Enterprise segment declined significantly in Q4. High churn and delayed onboarding milestones neutralized positive top-of-funnel activity.

## 2. EMEA Pipeline Illusion
EMEA sales reported a massive pipeline increase in Q4. However, conversion rates dropped below 10% and average sales cycle lengths stretched to over 160 days due to legal compliance delays, leaving recognized revenue flat.

## 3. FlowOps v2.0 Release Instability
The Q4 release of FlowOps v2.0 caused critical technical issues for high-throughput Enterprise clients, resulting in escalated tickets and temporary platform usage declines.

## 4. SMB Churn Escalation
SMB segment churn reached a peak of 20% due to ongoing support queue delays, completing a trend that started in Q2.
"""

    # 8. q4_apac_revenue_report.md
    docs['q4_apac_revenue_report'] = """---
doc_id: q4_apac_revenue_report
title: Q4 APAC Revenue Report
doc_type: regional_report
quarter: Q4_2025
region: APAC
segment: Enterprise
related_metrics:
  - recognized_revenue
  - churn_rate
  - marketing_spend
  - support_escalations
source: synthetic_internal_report
---

# Q4 APAC Revenue Report

Recognized revenue within the APAC Enterprise segment dropped significantly in Q4 2025. This downturn occurred despite a massive marketing spend spike targeting the region.

## The Revenue and Marketing Divergence
A marketing push in APAC drove pipeline interest, but recognized revenue declined. High churn rates (18.0%) among existing Enterprise accounts completely offset top-of-funnel conversion efforts.

## Onboarding and Technical Milestones
Several signed deals failed to reach the implementation milestones required to recognize revenue in Q4. This delay was exacerbated by FlowOps v2.0 stability issues, which halted data integrations for several APAC accounts.

## Timezone Support Constraints
Analysis indicates that APAC Enterprise support tickets experienced severe response delays. Due to coverage gaps, critical tickets remained in the queue for over 24 hours, driving customer dissatisfaction and accelerating cancellations.
"""

    # 9. pricing_change_memo.md
    docs['pricing_change_memo'] = """---
doc_id: pricing_change_memo
title: Pricing and Packaging Restructuring Memo
doc_type: policy_memo
quarter: Q3_2025
region: Global
segment: Enterprise
related_metrics:
  - churn_rate
  - recognized_revenue
source: synthetic_internal_policy
---

# Pricing and Packaging Restructuring Memo

This policy memo outlines the strategic packaging updates launched in late Q3 2025 and analyzes early customer friction.

## Structural Changes
We transitioned to a feature-gated packaging model. Basic visualization remains in InsightOS, but advanced connectors and orchestration in FlowOps are restricted to the Premium tier.

## Enterprise Segment Objections
While SMB and Mid-Market accounts adopted the pricing models, several APAC Enterprise clients objected to the forced migration to the Premium tier. This led directly to high-ARR churn events in Q4.

## Compliance and Renewal Warning
Sales representatives are cautioned not to offer ad-hoc pricing discounts to circumvent pricing blocks without executive approval. However, retention reports show that rigid enforcement of the new tiers is the primary driver of APAC Enterprise churn.
"""

    # 10. marketing_campaign_memo.md
    docs['marketing_campaign_memo'] = """---
doc_id: marketing_campaign_memo
title: Marketing Campaign Efficiency Memo
doc_type: policy_memo
quarter: Q4_2025
region: APAC
segment: Enterprise
related_metrics:
  - marketing_spend
  - pipeline_value
  - recognized_revenue
source: synthetic_internal_policy
---

# Marketing Campaign Efficiency Memo

This memo evaluates the efficiency of the APAC Enterprise Q4 demand generation campaign.

## Increased Spending Overview
Marketing spend in APAC was increased by 1.55x in Q4 to accelerate enterprise acquisition. While this push successfully generated leads, it failed to impact quarterly recognized revenue.

## Funnel Leakage Analysis
Leads generated by the campaign encountered severe friction in downstream engineering. Due to FlowOps platform instability in Q4, conversion timelines lengthened, preventing pipeline opportunities from converting to recognized revenue in the fiscal year.

## Key Recommendations
Future campaigns must align spend with technical readiness. Spending on marketing when core products are undergoing high-friction architecture updates results in low CAC efficiency.
"""

    # 11. support_escalation_report.md
    docs['support_escalation_report'] = """---
doc_id: support_escalation_report
title: Support Escalation and SLA Report
doc_type: operations_report
quarter: Q4_2025
region: Global
segment: All
related_metrics:
  - support_escalations
  - churn_rate
source: synthetic_internal_report
---

# Support Escalation and SLA Report

This report analyzes support performance across three major trouble spots during Q4 2025.

## 1. APAC Enterprise Timezone Issues
APAC Enterprise accounts suffered from severe SLA breaches in Q4. Initial response times reached an average of 24.8 hours due to timezone gaps. This lack of coverage was the primary driver of Q4 escalations.

## 2. SMB Ticket Delays
SMB support queues remained backlogged following support staff reassignments. Response times for SMB accounts averaged 32 hours, contributing to the 20% churn rate observed in Q4.

## 3. FlowOps Escalation Spike
The release of FlowOps v2.0 triggered a massive influx of High and Critical severity tickets. Because of the technical complexity of the release, all logged FlowOps tickets in Q4 required engineering escalation.
"""

    # 12. product_release_notes.md
    docs['product_release_notes'] = """---
doc_id: product_release_notes
title: Product Release Notes - FlowOps v2.0
doc_type: release_notes
quarter: Q4_2025
region: Global
segment: All
related_metrics:
  - usage_score
  - support_escalations
source: synthetic_internal_release
---

# Product Release Notes - FlowOps v2.0

These release notes detail the architectural updates introduced in the FlowOps v2.0 platform upgrade in Q4 2025.

## Major Ingestion Overhaul
FlowOps v2.0 introduced a multi-threaded execution queue designed to optimize high-volume data pipelines. This change increases parallel processing capacity for Enterprise scale data warehouses.

## Migration Requirements
Customers must update their API schemas to support the new thread pool model. Failure to update configurations before deployment may result in pipeline stalls or memory allocation errors.

## Post-Release Engineering Notes
We are monitoring pipeline stalls among Enterprise accounts. If performance issues occur, customer success teams should guide clients to implement temporary thread limits until a patch is deployed in Q1 2026.
"""

    # 13. customer_success_notes.md
    docs['customer_success_notes'] = """---
doc_id: customer_success_notes
title: Customer Success Retention Notes
doc_type: operations_report
quarter: Q3_2025
region: Global
segment: SMB
related_metrics:
  - usage_score
  - churn_rate
source: synthetic_internal_report
---

# Customer Success Retention Notes

This report highlights leading indicators of churn within the SMB segment observed during Q3 2025.

## Leading Indicators of Churn
Customer Success telemetry shows that usage scores drop significantly 45 to 60 days before a contract cancellation is finalized. A decrease in average sessions per account is the most accurate predictor of churn.

## Root Causes of Usage Decline
Friction in self-serve onboarding, combined with support response times exceeding 24 hours, is causing SMB accounts to stop using the software. Lacking rapid support, SMB clients turn off automated pipelines and abandon the platform.

## Proposed CS Interventions
We must automate alerts in our CRM when an SMB account's weekly usage score drops below 50. Reallocating support resources back to the general queue is necessary to resolve response delays.
"""

    # 14. emea_pipeline_review.md
    docs['emea_pipeline_review'] = """---
doc_id: emea_pipeline_review
title: EMEA Pipeline Performance Review
doc_type: regional_report
quarter: Q4_2025
region: EMEA
segment: Enterprise
related_metrics:
  - pipeline_value
  - conversion_rate
  - recognized_revenue
source: synthetic_internal_report
---

# EMEA Pipeline Performance Review

This review analyzes the variance between EMEA's massive pipeline expansion and its flat recognized revenue during Q4 2025.

## The EMEA Pipeline Growth
The sales pipeline in EMEA grew by 1.85x in Q4, signaling high demand. However, this growth was a "pipeline illusion" as actual recognized revenue remained completely flat.

## Declining Conversion Rates
Actual conversion rates dropped below 10% in Q4. Investigation shows that sales representatives registered speculative high-value opportunities to meet year-end pipeline generation quotas, inflating the forecast.

## Lengthening Sales Cycles
The average sales cycle duration for EMEA Enterprise accounts stretched past 160 days. New security and data privacy reviews slowed down procurement, preventing pipeline opportunities from converting to closed contracts.
"""

    # 15. smb_churn_review.md
    docs['smb_churn_review'] = """---
doc_id: smb_churn_review
title: SMB Churn In-Depth Review
doc_type: operations_report
quarter: Q4_2025
region: Global
segment: SMB
related_metrics:
  - churn_rate
  - support_escalations
  - usage_score
source: synthetic_internal_report
---

# SMB Churn In-Depth Review

This review analyzes the factors that drove SMB segment churn to an all-time high of 20.0% in Q4 2025.

## The Support Slowdown Correlation
Operational data confirms a correlation between support queue latency and SMB churn. Since the reallocation of support specialists in Q2, SMB ticket resolution times have remained elevated above 48 hours.

## Telemetry of Silent Churn
SMB clients encounter minor configuration errors, find support queues unresponsive, and gradually stop logging in. This results in a sharp drop in usage scores before they cancel their month-to-month contracts.

## Tactical Recommendations
We must establish a dedicated SMB support team. Resolving support response times is the single most critical factor required to stabilize SMB churn in 2026.
"""

    # 16. enterprise_retention_notes.md
    docs['enterprise_retention_notes'] = """---
doc_id: enterprise_retention_notes
title: Enterprise Segment Retention Analysis
doc_type: operations_report
quarter: Q4_2025
region: Global
segment: Enterprise
related_metrics:
  - churn_rate
  - support_escalations
  - usage_score
source: synthetic_internal_report
---

# Enterprise Segment Retention Analysis

This analysis reviews retention concerns within the Enterprise segment in Q4 2025, specifically focusing on APAC and FlowOps-related escalations.

## APAC Enterprise Churn
APAC Enterprise churn rose to 18% in Q4. Exit surveys indicate customer dissatisfaction with new feature gating and timezone support response delays.

## FlowOps v2.0 Integration Impact
The FlowOps v2.0 update caused high-volume pipeline failures for several large accounts. The resulting downtime forced clients to submit critical support escalations, impacting platform usage scores.

## Onboarding Delays
Onboarding teams report that FlowOps stability issues have delayed customer deployments, pushing back the milestone dates required to recognize revenue for newly signed contracts.
"""

    # 17. flowops_release_incident.md
    docs['flowops_release_incident'] = """---
doc_id: flowops_release_incident
title: FlowOps v2.0 Release Incident Report
doc_type: incident_report
quarter: Q4_2025
region: Global
segment: Enterprise
related_metrics:
  - usage_score
  - support_escalations
source: synthetic_internal_report
---

# FlowOps v2.0 Release Incident Report

This incident report details the technical failures and customer impact following the FlowOps v2.0 release in Q4 2025.

## Technical Failure Description
FlowOps v2.0 introduced a new thread-pool executor that encountered severe memory lock contention under high database query throughput. This contention caused automated ingestion pipelines to freeze.

## Customer Impact Summary
While SMB accounts with low data volumes were unaffected, Enterprise accounts experienced massive pipeline stalls. Many clients disabled automated FlowOps features, resulting in a 45% drop in Enterprise usage scores.

## Corrective Actions
Engineering has identified a patch to resolve the thread contention issue. Customer Success teams must work with Enterprise accounts to implement temporary configurations until the patch is deployed in Q1 2026.
"""

    # 18. sales_cycle_review.md
    docs['sales_cycle_review'] = """---
doc_id: sales_cycle_review
title: Sales Cycle and Velocity Review
doc_type: operations_report
quarter: Q4_2025
region: EMEA
segment: Enterprise
related_metrics:
  - pipeline_value
  - conversion_rate
source: synthetic_internal_report
---

# Sales Cycle and Velocity Review

This review analyzes the lengthening of the sales cycle for Enterprise accounts in EMEA during Q4 2025.

## Increase in Deal Cycle Duration
The average duration of EMEA Enterprise sales cycles stretched past 160 days in Q4, compared to a historical baseline of 90 days.

## Drivers of Cycle Latency
The primary driver of sales cycle latency was new regulatory compliance reviews. European clients required extensive GDPR audits and security reviews before signing contracts, delaying closures.

## Sales Pipeline Impact
Because deals remained stuck in legal review, EMEA's Q4 pipeline appeared inflated. This pipeline did not convert into closed contracts, leaving recognized revenue flat for the quarter.
"""

    # 19. customer_segment_guide.md
    docs['customer_segment_guide'] = """---
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
"""

    # 20. known_metric_confusions.md
    docs['known_metric_confusions'] = """---
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
"""

    for doc_id, content in docs.items():
        filepath = os.path.join('data/raw/unstructured', f"{doc_id}.md")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated {filepath}")

if __name__ == "__main__":
    create_unstructured_docs()
