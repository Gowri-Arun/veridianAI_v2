# NovaCloud Analytics - Schema Definitions

This document details the relational database schema representing NovaCloud Analytics' enterprise operations. It provides precise specifications for each table and documents key metric ambiguities to prevent analytical errors.

---

## Metric Confusions & Ambiguities

To perform accurate analysis on NovaCloud Analytics' data, it is critical to understand the following differences:

1. **Recognized Revenue is NOT Bookings**
   - *Bookings* represent the total committed contract value (TCV) signed by a client. No services have necessarily been delivered yet.
   - *Recognized Revenue* is the actual amount of money NovaCloud can declare as earned under accounting principles (ASC 606) when service milestones or time-based subscription delivery actually occur. A $120,000 annual booking in Q4 recognizes only $10,000 of revenue in Q4 (assuming straight-line recognition).

2. **Bookings are NOT Pipeline**
   - *Pipeline* is the total estimated value of active sales opportunities currently being pursued. It is speculative.
   - *Bookings* are finalized, legally binding signed contracts (Closed-Won deals).

3. **Pipeline is NOT Guaranteed Revenue**
   - Pipeline values are weighted or unweighted expectations of future sales. Deals in the pipeline can be lost (Closed-Lost) or have their deal sizes drastically reduced during negotiation.

4. **Churn is NOT the Same as Support Tickets**
   - *Support Tickets* reflect operational friction and customer queries.
   - *Churn* is the ultimate failure event—the loss of the customer contract and its associated ARR. High support ticket volume/latency is a *leading indicator* of churn, but not every ticket leads to churn, and some customers churn silently without submitting tickets.

5. **Marketing Spend Does NOT Always Cause Revenue Growth**
   - There is often a significant time lag (2 to 4 quarters) between marketing spend and recognized revenue due to sales cycle lengths. Additionally, bad targeting, poor product releases, or pricing issues can completely neutralize marketing investments.

6. **ARR is NOT Quarterly Recognized Revenue**
   - *Annual Recurring Revenue (ARR)* represents the annualized run-rate of recurring subscription contracts active at a point in time (e.g., $10,000 recurring monthly fee = $120,000 ARR).
   - *Quarterly Recognized Revenue* is the historical amount actually earned during that specific 3-month period, which can include non-recurring setup fees, seasonal adjustments, and credits.

---

## Database Schema

### 1. `revenue`
- **Purpose**: Records historical quarterly recognized revenue by customer, product, region, segment, and quarter.
- **Columns**:
  - `revenue_id` (VARCHAR, PRIMARY KEY): Unique identifier for the revenue record.
  - `customer_id` (VARCHAR, FOREIGN KEY): Links to `customers`.
  - `product_id` (VARCHAR): The specific product tier or module (InsightOS, MetricHub, FlowOps).
  - `region` (VARCHAR): The geographic region (APAC, EMEA, NA, LATAM).
  - `segment` (VARCHAR): The customer segment (SMB, Mid-Market, Enterprise).
  - `quarter` (VARCHAR): The time period (Q1_2025, Q2_2025, etc.).
  - `amount` (DECIMAL): The actual recognized revenue amount in USD.
- **Known Ambiguity**: This table represents recognized revenue, which differs from bookings. If a customer churns mid-quarter, their recognized revenue may still be non-zero for that quarter up to the termination date.

### 2. `customers`
- **Purpose**: Details core customer profiles, segment classification, geographical location, and date of first acquisition.
- **Columns**:
  - `customer_id` (VARCHAR, PRIMARY KEY): Unique customer identifier.
  - `customer_name` (VARCHAR): Name of the client organization.
  - `segment` (VARCHAR): SMB, Mid-Market, or Enterprise.
  - `region` (VARCHAR): APAC, EMEA, NA, or LATAM.
  - `signup_quarter` (VARCHAR): The quarter the customer originally signed up (e.g., Q1_2025).
  - `status` (VARCHAR): Customer health status (Active, Churned).
- **Known Ambiguity**: Customers can change segments over time (e.g., growing from Mid-Market to Enterprise), but this table captures their current status. Historical segment mappings may require analyzing transaction or historical logs.

### 3. `marketing_spend`
- **Purpose**: Tracks operational marketing budget allocation by region, target segment, and quarter.
- **Columns**:
  - `spend_id` (VARCHAR, PRIMARY KEY): Unique record identifier.
  - `quarter` (VARCHAR): Time period.
  - `region` (VARCHAR): Region targeted by the campaign.
  - `segment` (VARCHAR): Customer segment targeted.
  - `channel` (VARCHAR): The medium (Events, Paid Search, Content, Outbound).
  - `amount` (DECIMAL): The marketing spend in USD.
- **Known Ambiguity**: Marketing spend is hard to attribute cleanly. A global marketing campaign may target APAC and EMEA jointly, but the spend is split arbitrarily or assigned to a single region.

### 4. `churn`
- **Purpose**: Logs contract cancellation events and the associated ARR lost.
- **Columns**:
  - `churn_id` (VARCHAR, PRIMARY KEY): Unique churn record identifier.
  - `customer_id` (VARCHAR, FOREIGN KEY): Links to `customers`.
  - `churn_quarter` (VARCHAR): The quarter in which the churn event was finalized.
  - `arr_lost` (DECIMAL): The ARR value lost due to this cancellation.
  - `reason` (VARCHAR): Categorized reason (Pricing, Competitor, Support, Product Instability, Out of Business).
- **Known Ambiguity**: A customer might cancel their subscription (churn) in Q3, but because they paid in advance, they continue using the product until Q4. The churn event date is when the contract terminates, not necessarily when the decision was communicated.

### 5. `support_tickets`
- **Purpose**: Captures customer support operational metrics, tracking resolution times and escalation events.
- **Columns**:
  - `ticket_id` (VARCHAR, PRIMARY KEY): Unique ticket identifier.
  - `customer_id` (VARCHAR, FOREIGN KEY): Links to `customers`.
  - `product_id` (VARCHAR): Product associated with the issue.
  - `quarter` (VARCHAR): The quarter the ticket was created.
  - `severity` (VARCHAR): Low, Medium, High, or Critical.
  - `is_escalated` (BOOLEAN): TRUE if the ticket required engineering or executive escalation.
  - `response_time_hours` (DECIMAL): Hours elapsed from ticket creation to first human response.
  - `resolution_time_hours` (DECIMAL): Total hours elapsed until ticket closure.
- **Known Ambiguity**: A high response time doesn't always mean a poor customer experience (e.g., if the problem was extremely complex), but it acts as a strong statistical proxy.

### 6. `product_usage`
- **Purpose**: Monitors feature adoption, user activity, and technical performance indicators.
- **Columns**:
  - `usage_id` (VARCHAR, PRIMARY KEY): Unique usage record identifier.
  - `customer_id` (VARCHAR, FOREIGN KEY): Links to `customers`.
  - `product_id` (VARCHAR): InsightOS, MetricHub, or FlowOps.
  - `quarter` (VARCHAR): Time period.
  - `active_users_count` (INTEGER): Number of unique monthly active users (MAU).
  - `features_used` (INTEGER): Number of distinct advanced product features activated.
  - `api_error_count` (INTEGER): Number of failed API calls or pipeline errors encountered.
- **Known Ambiguity**: A customer can have high product usage but still churn if they are performing operations inefficiently, encountering high error rates, or are unhappy with price.

### 7. `sales_pipeline`
- **Purpose**: Tracks potential sales opportunities, stages, deal values, and cycle times.
- **Columns**:
  - `opportunity_id` (VARCHAR, PRIMARY KEY): Unique opportunity identifier.
  - `customer_name` (VARCHAR): Name of prospective client organization.
  - `region` (VARCHAR): Geolocation.
  - `segment` (VARCHAR): Target segment.
  - `quarter` (VARCHAR): Quarter the opportunity was created or updated.
  - `stage` (VARCHAR): Current funnel stage (Prospecting, Qualification, Proposal, Negotiation, Closed-Won, Closed-Lost).
  - `deal_value` (DECIMAL): Estimated annual contract value of the deal.
  - `deal_cycle_days` (INTEGER): Days elapsed since opportunity creation.
  - `win_probability` (DECIMAL): Likelihood of closing (0.00 to 1.00).
- **Known Ambiguity**: Representatives may manipulate `win_probability` or `deal_value` to satisfy administrative pipeline requirements, making historical conversions and cycle lengths a better predictor of actual sales.

### 8. `subscriptions`
- **Purpose**: Manages active contract terms, annual contract values, and renewal dates.
- **Columns**:
  - `subscription_id` (VARCHAR, PRIMARY KEY): Unique subscription ID.
  - `customer_id` (VARCHAR, FOREIGN KEY): Links to `customers`.
  - `product_id` (VARCHAR): Product being licensed.
  - `arr` (DECIMAL): Annual Recurring Revenue rate of the contract.
  - `start_date` (DATE): Contract start date.
  - `end_date` (DATE): Contract end/renewal date.
- **Known Ambiguity**: Subscriptions with multi-year terms might have flat ARR figures but escalating billing structures (e.g., $100k Year 1, $110k Year 2), which is not captured in a simple static ARR field.

### 9. `region_targets`
- **Purpose**: Sets performance benchmarks for ARR goals per region, customer segment, and quarter.
- **Columns**:
  - `target_id` (VARCHAR, PRIMARY KEY): Unique target record ID.
  - `quarter` (VARCHAR): Target time period.
  - `region` (VARCHAR): Target region.
  - `segment` (VARCHAR): Target customer segment.
  - `target_arr` (DECIMAL): The target ARR goal in USD.
- **Known Ambiguity**: Region targets are static expectations and are sometimes adjusted mid-year due to macroeconomic changes, which can lead to target discrepancy versions.
