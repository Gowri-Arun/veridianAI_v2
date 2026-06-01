# NovaCloud Analytics — Schema Definitions

This document defines every table in the relational data world, with column types, purpose, known ambiguities, and cross-table relationships.

---

## Metric Confusions & Ambiguities

These six distinctions are critical for correct analysis. The dataset deliberately blurs them to test whether the system can disambiguate:

1. **Recognized Revenue is NOT Bookings**
   - Recognized Revenue = money earned under ASC 606 based on delivered services.
   - Bookings = signed contract value (TCV/ACV). A $120K annual contract booked in Q4 recognizes only ~$10K in Q4 under straight-line recognition.

2. **Bookings are NOT Pipeline**
   - Bookings are closed-won, legally binding commitments.
   - Pipeline is speculative — opportunities that may or may not close.

3. **Pipeline is NOT Guaranteed Revenue**
   - Pipeline can be inflated, stale, or lost. Weighted pipeline gives a more realistic view, but even that is not reliable.

4. **Churn is NOT the Same as Support Tickets**
   - Support tickets are operational events; churn is a terminal contract outcome.
   - High support volume/latency is a *leading indicator* of churn, but not all tickets lead to churn, and some churn happens without any tickets.

5. **Marketing Spend Does NOT Always Cause Revenue Growth**
   - Marketing investment may take 2–4 quarters to convert to revenue. Poor retention, pricing issues, or product quality can completely neutralize it.

6. **ARR is NOT Quarterly Recognized Revenue**
   - ARR = annualized run-rate of active subscriptions at a point in time.
   - Quarterly recognized revenue = actual earnings in that 3-month window, which includes one-time fees, credits, and partial-quarter effects.

---

## Table Definitions

### 1. `revenue`

| Column       | Type         | Description                                           |
|--------------|--------------|-------------------------------------------------------|
| revenue_id   | VARCHAR(20)  | Primary key, e.g. `REV-APAC-EN-2025-Q4-001`           |
| customer_id  | VARCHAR(20)  | Foreign key → `customers.customer_id`                  |
| product_id   | VARCHAR(20)  | One of `InsightOS`, `MetricHub`, `FlowOps`             |
| region       | VARCHAR(10)  | APAC, EMEA, NA, LATAM                                  |
| segment      | VARCHAR(15)  | SMB, Mid-Market, Enterprise                            |
| quarter      | VARCHAR(10)  | Q1_2025, Q2_2025, Q3_2025, Q4_2025                    |
| amount       | DECIMAL(12,2)| Recognized revenue in USD                              |

**Purpose**: Records historical quarterly recognized revenue at customer-product granularity.

**Known Ambiguity**: If a customer churns mid-quarter, their recognized revenue for that quarter may be non-zero up to the termination date. Also, one-time setup fees and credits are included in `amount`, making it not purely recurring.

---

### 2. `customers`

| Column          | Type         | Description                                  |
|-----------------|--------------|----------------------------------------------|
| customer_id     | VARCHAR(20)  | Primary key, e.g. `CUST-APAC-SMB-001`         |
| customer_name   | VARCHAR(100) | Client organization name                      |
| segment         | VARCHAR(15)  | SMB, Mid-Market, Enterprise                   |
| region          | VARCHAR(10)  | APAC, EMEA, NA, LATAM                         |
| signup_quarter  | VARCHAR(10)  | Quarter of first subscription (e.g. Q1_2025)  |
| status          | VARCHAR(10)  | Active or Churned                             |

**Purpose**: Core customer profile data.

**Known Ambiguity**: Customers may change segments over time (e.g., a Mid-Market firm grows into Enterprise). This table stores the *current* or *latest known* segment. Historical analysis must use `revenue` or `subscriptions` tables for per-quarter segment attribution.

---

### 3. `marketing_spend`

| Column    | Type         | Description                                      |
|-----------|--------------|--------------------------------------------------|
| spend_id  | VARCHAR(20)  | Primary key, e.g. `SPND-NA-EN-2025-Q1-001`        |
| quarter   | VARCHAR(10)  | Time period                                       |
| region    | VARCHAR(10)  | Target region                                     |
| segment   | VARCHAR(15)  | Target segment                                    |
| channel   | VARCHAR(20)  | Events, Paid Search, Content, Outbound            |
| amount    | DECIMAL(12,2)| Spend amount in USD                                |

**Purpose**: Captures marketing budget deployment by target region, segment, and channel.

**Known Ambiguity**: Spend attribution is inherently fuzzy. A global brand campaign may be split arbitrarily across regions. This table records the *planned allocation*, which may not perfectly match actual regional impact.

---

### 4. `churn`

| Column         | Type         | Description                                       |
|----------------|--------------|----------------------------------------------------|
| churn_id       | VARCHAR(20)  | Primary key, e.g. `CHRN-APAC-EN-2025-Q4-001`       |
| customer_id    | VARCHAR(20)  | Foreign key → `customers.customer_id`               |
| churn_quarter  | VARCHAR(10)  | Quarter the churn was finalized                     |
| arr_lost       | DECIMAL(12,2)| ARR lost from this churn event                      |
| reason         | VARCHAR(25)  | Pricing, Competitor, Support, Product Instability, Out of Business |

**Purpose**: Logs contract cancellation events and their associated ARR impact.

**Known Ambiguity**: Churn quarter is when the contract *ended*, not when the customer *decided* to leave. The decision may have been made 1–2 quarters earlier (visible through usage decline or support tickets). Also, a customer may churn from one product but keep another.

---

### 5. `support_tickets`

| Column                | Type         | Description                                        |
|-----------------------|--------------|----------------------------------------------------|
| ticket_id             | VARCHAR(20)  | Primary key, e.g. `TKT-NA-SMB-2025-Q1-0001`         |
| customer_id           | VARCHAR(20)  | Foreign key → `customers.customer_id`               |
| product_id            | VARCHAR(20)  | InsightOS, MetricHub, FlowOps                       |
| quarter               | VARCHAR(10)  | Quarter the ticket was opened                        |
| severity              | VARCHAR(10)  | Low, Medium, High, Critical                          |
| is_escalated          | BOOLEAN      | TRUE if escalated to engineering/exec                |
| response_time_hours   | DECIMAL(8,2) | Hours from creation to first human response          |
| resolution_time_hours | DECIMAL(8,2) | Hours from creation to ticket closure                |

**Purpose**: Tracks support operational metrics — responsiveness, escalation rates, and resolution efficiency.

**Known Ambiguity**: High response time may indicate either poor service or an extremely complex issue that required research. Missing tickets (customers who left without submitting) are not captured. A drop in ticket volume may mean service improved — or that customers gave up.

---

### 6. `product_usage`

| Column             | Type         | Description                                          |
|--------------------|--------------|------------------------------------------------------|
| usage_id           | VARCHAR(20)  | Primary key, e.g. `USG-NA-MID-2025-Q1-001`            |
| customer_id        | VARCHAR(20)  | Foreign key → `customers.customer_id`                 |
| product_id         | VARCHAR(20)  | InsightOS, MetricHub, FlowOps                         |
| quarter            | VARCHAR(10)  | Time period                                           |
| active_users_count | INT          | Monthly active users (MAU) for that quarter            |
| features_used      | INT          | Number of distinct advanced features used              |
| api_error_count    | INT          | Failed API calls or pipeline errors                    |

**Purpose**: Monitors product adoption, engagement depth, and technical health.

**Known Ambiguity**: High usage does not guarantee satisfaction (users may be forced to use a buggy product). Low usage may indicate churn risk or seasonal patterns. `api_error_count` is a leading indicator for support escalations and churn.

---

### 7. `sales_pipeline`

| Column          | Type         | Description                                         |
|-----------------|--------------|-----------------------------------------------------|
| opportunity_id  | VARCHAR(20)  | Primary key, e.g. `OPP-EMEA-EN-2025-Q4-001`          |
| customer_name   | VARCHAR(100) | Prospective client name (not yet an FK to customers) |
| region          | VARCHAR(10)  | Geographic region                                    |
| segment         | VARCHAR(15)  | Target segment                                       |
| quarter         | VARCHAR(10)  | Quarter the opportunity was created/updated           |
| stage           | VARCHAR(20)  | Prospecting, Qualification, Proposal, Negotiation, Closed-Won, Closed-Lost |
| deal_value      | DECIMAL(12,2)| Estimated annual contract value                      |
| deal_cycle_days | INT          | Days since opportunity creation                       |
| win_probability | DECIMAL(3,2) | Estimated close likelihood (0.00 to 1.00)            |

**Purpose**: Tracks sales opportunities through the funnel from prospecting to close.

**Known Ambiguity**: `customer_name` is free text, not a foreign key — prospects may not yet exist in `customers`. `win_probability` is often inflated by sales reps. `deal_value` may be speculative, especially under pipeline generation pressure. Historical conversion rates and cycle lengths are more reliable than stated win probabilities.

---

### 8. `subscriptions`

| Column          | Type         | Description                                      |
|-----------------|--------------|--------------------------------------------------|
| subscription_id | VARCHAR(20)  | Primary key, e.g. `SUB-APAC-EN-2025-001`          |
| customer_id     | VARCHAR(20)  | Foreign key → `customers.customer_id`             |
| product_id      | VARCHAR(20)  | InsightOS, MetricHub, FlowOps                     |
| arr             | DECIMAL(12,2)| Annual Recurring Revenue rate                     |
| start_date      | DATE         | Contract start date                                |
| end_date        | DATE         | Contract end / renewal date                        |

**Purpose**: Manages active contract terms, ARR rates, and renewal timelines.

**Known Ambiguity**: Multi-year contracts may have escalating pricing (e.g., $100K Y1, $110K Y2) not captured in a single static `arr` field. A customer may have multiple active subscriptions for different products. `end_date` before the end of a quarter does not guarantee churn — the contract may be in renewal negotiation.

---

### 9. `region_targets`

| Column     | Type         | Description                                       |
|------------|--------------|---------------------------------------------------|
| target_id  | VARCHAR(20)  | Primary key, e.g. `TGT-NA-SMB-2025-Q1`             |
| quarter    | VARCHAR(10)  | Target time period                                  |
| region     | VARCHAR(10)  | Target region                                       |
| segment    | VARCHAR(15)  | Target customer segment                             |
| target_arr | DECIMAL(12,2)| Target ARR goal in USD                               |

**Purpose**: Sets quarterly ARR performance targets by region and segment for measuring plan vs. actual.

**Known Ambiguity**: Targets are static expectations set at the beginning of the fiscal year. They may be adjusted mid-year (e.g., due to macroeconomic changes), creating versioning discrepancies. Comparing recognized revenue against target_arr requires understanding revenue recognition timing.

---

## Cross-Table Relationship Map

| From               | To                 | Via                    | Relationship |
|--------------------|--------------------|------------------------|--------------|
| `revenue`          | `customers`        | `customer_id`          | M:1          |
| `subscriptions`    | `customers`        | `customer_id`          | M:1          |
| `churn`            | `customers`        | `customer_id`          | M:1          |
| `support_tickets`  | `customers`        | `customer_id`          | M:1          |
| `product_usage`    | `customers`        | `customer_id`          | M:1          |
| `revenue`          | `subscriptions`    | `customer_id`          | M:M (indirect via customer) |

**Tables without direct FKs**: `sales_pipeline` (uses `customer_name` text), `marketing_spend` (filter-based joins on region + segment), `region_targets` (filter-based joins on region + segment + quarter).

---

## Narrative-to-Table Mapping

| Narrative                          | Primary Tables                                    | Secondary Tables             |
|------------------------------------|---------------------------------------------------|------------------------------|
| APAC Enterprise Revenue Drop       | `revenue`, `churn`, `support_tickets`             | `marketing_spend`, `subscriptions`, `sales_pipeline` |
| EMEA Pipeline Illusion             | `sales_pipeline`, `revenue`                      | `region_targets`, `subscriptions` |
| SMB Churn After Support Slowdown   | `churn`, `support_tickets`, `product_usage`       | `revenue`                    |
| FlowOps Release Side Effect        | `product_usage`, `support_tickets`, `revenue`     | `churn`                      |
