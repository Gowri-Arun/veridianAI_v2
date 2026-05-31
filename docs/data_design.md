# NovaCloud Analytics - Enterprise Data Design

## Company Overview
NovaCloud Analytics is a leading provider of a next-generation B2B SaaS analytics platform. The company's mission is to empower data-driven decisions by providing real-time data ingestion, transformation, and business intelligence capabilities directly integrated into enterprise workflows.

### Products
- **InsightOS**: The core operating system for data visualization, dashboarding, and interactive reporting. It serves as the main user interface and entry point for daily analytical tasks.
- **MetricHub**: A centralized metric store and semantic layer that ensures a single source of truth for key performance indicators (KPIs) across various departments.
- **FlowOps**: A data orchestration and ingestion engine designed to automate pipelines, manage ETL processes, and monitor data health in real time.

### Regions
- **APAC** (Asia-Pacific)
- **EMEA** (Europe, Middle East, and Africa)
- **North America** (NA)
- **LATAM** (Latin America)

### Customer Segments
- **SMB** (Small and Medium-sized Businesses): Typically high transaction count, low deal size, shorter sales cycles, and self-serve onboarding.
- **Mid-Market**: Moderate deal size, hybrid high-touch and self-serve, and steady growth potential.
- **Enterprise**: High-value annual contracts, long sales cycles, highly customized integrations, and dedicated Customer Success Manager (CSM) support.

### Time Periods
- **Q1_2025**
- **Q2_2025**
- **Q3_2025**
- **Q4_2025**

---

## Core Business Metrics
To accurately evaluate NovaCloud's health, we track a set of fundamental operational metrics:
- **Recognized Revenue**: Revenue recognized in a quarter for services actually delivered. Not to be confused with billings or contract signings.
- **Bookings**: The total contract value (TCV) or annual contract value (ACV) of signed customer agreements. Represents committed future revenue, but is not recognized immediately.
- **Sales Pipeline**: The aggregate value of potential deals at various stages of the sales cycle (e.g., Prospecting, Qualification, Proposal, Negotiation).
- **Annual Recurring Revenue (ARR)**: The annualized value of recurring revenue from active subscriptions.
- **Churn Rate**: The percentage of revenue (Gross/Net Revenue Churn) or customers (Customer Churn) lost over a given period.
- **Retention Rate**: The percentage of revenue or customers retained (Net Retention Rate - NRR, Gross Retention Rate - GRR).
- **Marketing Spend**: Financial resources allocated to demand generation, paid campaigns, events, and advertising.
- **Conversion Rate**: The percentage of pipeline deals or marketing leads that successfully convert into signed customers.
- **Support Escalations / Tickets**: The frequency and severity of support cases submitted by customers. High response time and ticket volumes correlate strongly with churn.
- **Product Usage / Adoption**: Weekly/Monthly Active Users (WAU/MAU) and feature-specific interactions (e.g., pipeline runs in FlowOps, dashboard views in InsightOS).

---

## Data Architecture & Design Principles

### Design Principles
1. **Internal Consistency**: All metrics across structured tables and unstructured documents must be cross-referencable. For example, if a narrative discusses a revenue dip in Q4_2025 for APAC Enterprise, the underlying `revenue`, `customers`, and `support_tickets` tables must quantitatively reflect this.
2. **Realism**: Data must simulate real SaaS dynamics, such as seasonal effects, support latency, customer churn following product issues, and delayed conversions.
3. **Traceability**: Every qualitative business narrative must have a quantitative "breadcrumb trail" through keys such as `region`, `segment`, `product_id`, and `quarter`.

### Structured Tables defined in the Schema
- **`revenue`**: Records quarterly recognized revenue details.
- **`customers`**: Details customer metadata, segment, region, and signup status.
- **`marketing_spend`**: Tracks outbound spend by region, segment, and quarter.
- **`churn`**: Logs customer churn events, reasons, and associated ARR loss.
- **`support_tickets`**: Tracks customer support requests, resolution times, and escalations.
- **`product_usage`**: Captures adoption metrics, active users, and API error counts.
- **`sales_pipeline`**: Logs pipeline opportunities, stages, deal sizes, and cycle lengths.
- **`subscriptions`**: Manages contract terms, recurring fees, and products purchased.
- **`region_targets`**: Stores expected ARR targets per region and segment to measure performance.

### Unstructured Documents
The data world is enriched with unstructured contexts:
- **QBR (Quarterly Business Review) Presentations**: PDF/text summaries of regional performances.
- **Support Escalation Logs**: Transcripts and post-mortems of critical service disruptions.
- **Product Release Notes**: Logs documenting major product rollouts and stability issues.
- **Internal Slack/Email Communications**: Contextualizing sudden changes in client sentiment or sales cycle delays.

---

## Hidden Business Narratives Overview
The dataset contains four specific complex scenarios that require multi-table joining and unstructured document analysis to properly diagnose:
1. **APAC Enterprise Revenue Drop**: Q4_2025 revenue decline driven by high-touch support issues and churn post-pricing change.
2. **EMEA Pipeline Illusion**: A misleading pipeline surge in Q4_2025 that masked declining conversion rates and longer sales cycles.
3. **SMB Churn After Support Slowdown**: Q3/Q4_2025 SMB churn spike directly trailing increased support response times and dropping product usage.
4. **FlowOps Release Side Effect**: A major Q4_2025 FlowOps update that caused system instability and subsequent Enterprise client friction.

*(For detailed breakdowns of these stories, please see [business_narratives.md](file:///c:/Users/gowri/veridianAI_v2/docs/business_narratives.md))*
