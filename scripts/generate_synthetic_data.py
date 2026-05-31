import os
import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Constants
QUARTERS = ['Q1_2025', 'Q2_2025', 'Q3_2025', 'Q4_2025']
REGIONS = ['APAC', 'EMEA', 'North America', 'LATAM']
SEGMENTS = ['SMB', 'Mid-Market', 'Enterprise']
PRODUCTS = ['InsightOS', 'MetricHub', 'FlowOps']
CHANNELS = ['Events', 'Paid Search', 'Content']
INDUSTRIES = ['Tech', 'Finance', 'Healthcare', 'Retail', 'Logistics', 'Education']

def ensure_directories():
    os.makedirs('data/raw/structured', exist_ok=True)

def generate_customers():
    # We want between 300 and 500 rows for customers.csv
    # Let's generate exactly 400 customers.
    num_customers = 400
    customer_ids = [f"CUST_{i:03d}" for i in range(1, num_customers + 1)]
    
    # Distribute regions and segments
    cust_regions = np.random.choice(REGIONS, num_customers, p=[0.25, 0.30, 0.30, 0.15])
    cust_segments = np.random.choice(SEGMENTS, num_customers, p=[0.50, 0.35, 0.15])
    cust_industries = np.random.choice(INDUSTRIES, num_customers)
    cust_signups = np.random.choice(QUARTERS, num_customers, p=[0.30, 0.25, 0.25, 0.20])
    
    # Determine status: most are active, but we introduce churned customers
    # in accordance with the narratives:
    # - APAC Enterprise churned in Q4_2025
    # - SMB churned in Q3_2025 and Q4_2025
    status_list = []
    for r, s, q in zip(cust_regions, cust_segments, cust_signups):
        # Default behavior: low chance of churn
        churn_chance = 0.05
        
        # Narrative 1: APAC Enterprise churn in late 2025
        if r == 'APAC' and s == 'Enterprise':
            churn_chance = 0.30
            
        # Narrative 3: SMB churn spike in Q3/Q4_2025
        elif s == 'SMB':
            churn_chance = 0.25
            
        if np.random.rand() < churn_chance:
            status_list.append('Churned')
        else:
            status_list.append('Active')
            
    customer_names = [f"{ind}_{cid.split('_')[1]}" for ind, cid in zip(cust_industries, customer_ids)]
    
    df_customers = pd.DataFrame({
        'customer_id': customer_ids,
        'customer_name': customer_names,
        'region': cust_regions,
        'segment': cust_segments,
        'industry': cust_industries,
        'signup_quarter': cust_signups,
        'status': status_list
    })
    
    return df_customers

def generate_subscriptions(df_customers):
    # We want between 300 and 500 rows. Let's generate one subscription per customer.
    # To make it more realistic, some active customers might have multiple product subscriptions.
    # Let's generate subscriptions based on customer profile.
    subscriptions = []
    sub_id_counter = 1
    
    for _, row in df_customers.iterrows():
        cid = row['customer_id']
        seg = row['segment']
        signup_q = row['signup_quarter']
        status = row['status']
        
        # Determine number of products subscribed
        # Enterprise typically subscribes to more products
        if seg == 'Enterprise':
            num_subs = np.random.choice([1, 2, 3], p=[0.3, 0.5, 0.2])
        elif seg == 'Mid-Market':
            num_subs = np.random.choice([1, 2], p=[0.7, 0.3])
        else:
            num_subs = 1
            
        chosen_products = np.random.choice(PRODUCTS, size=num_subs, replace=False)
        
        for prod in chosen_products:
            # Plan type
            if seg == 'Enterprise':
                plan = 'Premium Enterprise'
                base_arr = 120000.0 + np.random.uniform(-10000, 20000)
            elif seg == 'Mid-Market':
                plan = 'Professional'
                base_arr = 36000.0 + np.random.uniform(-5000, 5000)
            else:
                plan = 'Standard'
                base_arr = 12000.0 + np.random.uniform(-2000, 2000)
                
            # If the customer is churned, mark subscription as cancelled or active based on quarter
            sub_status = 'Active'
            renewal_q = 'Q1_2026'
            
            if status == 'Churned':
                # Churn occurs after signup.
                sub_status = 'Cancelled'
                if signup_q == 'Q1_2025':
                    renewal_q = np.random.choice(['Q2_2025', 'Q3_2025', 'Q4_2025'], p=[0.2, 0.4, 0.4])
                elif signup_q == 'Q2_2025':
                    renewal_q = np.random.choice(['Q3_2025', 'Q4_2025'], p=[0.4, 0.6])
                else:
                    renewal_q = 'Q4_2025'
            
            subscriptions.append({
                'subscription_id': f"SUB_{sub_id_counter:03d}",
                'customer_id': cid,
                'product': prod,
                'plan_type': plan,
                'start_quarter': signup_q,
                'renewal_quarter': renewal_q,
                'arr': round(base_arr, 2),
                'status': sub_status
            })
            sub_id_counter += 1
            
    df_subs = pd.DataFrame(subscriptions)
    return df_subs

def generate_revenue():
    # Exactly 144 rows: 4 quarters × 4 regions × 3 segments × 3 products
    rows = []
    for q in QUARTERS:
        for r in REGIONS:
            for s in SEGMENTS:
                for p in PRODUCTS:
                    # Baseline revenue generation values
                    if s == 'Enterprise':
                        base_rev = 150000.0
                        base_bookings = 180000.0
                        base_pipe = 500000.0
                        margin = 0.82
                    elif s == 'Mid-Market':
                        base_rev = 60000.0
                        base_bookings = 70000.0
                        base_pipe = 200000.0
                        margin = 0.78
                    else:  # SMB
                        base_rev = 30000.0
                        base_bookings = 32000.0
                        base_pipe = 90000.0
                        margin = 0.70
                        
                    # Add standard quarter-over-quarter growth
                    q_idx = QUARTERS.index(q)
                    growth_factor = 1.0 + (q_idx * 0.08)
                    rev = base_rev * growth_factor * np.random.uniform(0.95, 1.05)
                    bookings = base_bookings * growth_factor * np.random.uniform(0.90, 1.10)
                    pipe = base_pipe * growth_factor * np.random.uniform(0.90, 1.10)
                    
                    # Narrative 1: APAC Enterprise Q4 Revenue Drop
                    if q == 'Q4_2025' and r == 'APAC' and s == 'Enterprise':
                        # Recognized revenue drops compared to Q3
                        # Let's explicitly force it down. In Q3 it grew, in Q4 it drops below Q3.
                        rev = base_rev * 0.80  # Drop below Q1 base
                        # Bookings might remain flat or drop slightly
                        bookings = base_bookings * 0.95
                        # Gross margin declines slightly due to excessive support effort
                        margin = 0.74
                        
                    # Narrative 2: EMEA Pipeline Illusion in Q4_2025
                    if q == 'Q4_2025' and r == 'EMEA':
                        # Pipeline value increases significantly
                        pipe = base_pipe * 1.6
                        # recognized revenue stays flat or slightly declines compared to Q3
                        rev = base_rev * 1.05 * 0.92  # flat/down
                        
                    # Narrative 3: SMB Churn After Support Slowdown in Q3 & Q4
                    if s == 'SMB' and q in ['Q3_2025', 'Q4_2025']:
                        # Revenue takes a hit due to high SMB churn
                        rev = rev * 0.82
                        
                    # Narrative 4: FlowOps Release Side Effect in Q4_2025
                    if q == 'Q4_2025' and p == 'FlowOps':
                        # High churn/credits reduces recognized revenue
                        rev = rev * 0.85
                        margin = margin - 0.04
                        
                    rows.append({
                        'quarter': q,
                        'region': r,
                        'segment': s,
                        'product': p,
                        'recognized_revenue': round(rev, 2),
                        'bookings': round(bookings, 2),
                        'pipeline_value': round(pipe, 2),
                        'gross_margin': round(margin, 3)
                    })
                    
    return pd.DataFrame(rows)

def generate_marketing_spend():
    # Exactly 48 rows: 4 quarters × 4 regions × 3 channels
    rows = []
    for q in QUARTERS:
        for r in REGIONS:
            for c in CHANNELS:
                # Baseline spend
                base_spend = 15000.0
                q_idx = QUARTERS.index(q)
                spend = base_spend * (1.0 + q_idx * 0.1) * np.random.uniform(0.9, 1.1)
                
                # Narrative 1: APAC Enterprise Q4 Revenue Drop
                # "APAC Enterprise recognized revenue declined in Q4_2025 despite increased marketing spend."
                if q == 'Q4_2025' and r == 'APAC':
                    spend = spend * 1.55  # Clear increase in marketing spend
                    
                # Narrative 2: EMEA Pipeline Illusion in Q4_2025
                if q == 'Q4_2025' and r == 'EMEA':
                    spend = spend * 1.30
                    
                leads = int(spend / np.random.uniform(80, 120))
                campaign_name = f"Campaign_{r}_{c}_{q.split('_')[0]}"
                
                rows.append({
                    'quarter': q,
                    'region': r,
                    'channel': c,
                    'spend': round(spend, 2),
                    'campaign_name': campaign_name,
                    'leads_generated': leads
                })
                
    return pd.DataFrame(rows)

def generate_churn():
    # Exactly 48 rows: 4 quarters × 4 regions × 3 segments
    rows = []
    for q in QUARTERS:
        for r in REGIONS:
            for s in SEGMENTS:
                # Baseline metrics
                if s == 'Enterprise':
                    starting_custs = 20
                    base_churn_rate = 0.02
                elif s == 'Mid-Market':
                    starting_custs = 50
                    base_churn_rate = 0.05
                else:  # SMB
                    starting_custs = 150
                    base_churn_rate = 0.06
                    
                q_idx = QUARTERS.index(q)
                starting_custs = int(starting_custs * (1.0 + q_idx * 0.08))
                
                churn_rate = base_churn_rate * np.random.uniform(0.8, 1.2)
                
                # Narrative 1: APAC Enterprise Q4 Revenue Drop
                # "churn_rate should increase"
                if q == 'Q4_2025' and r == 'APAC' and s == 'Enterprise':
                    churn_rate = 0.18  # Sharp spike
                    
                # Narrative 3: SMB Churn After Support Slowdown
                # "For SMB in Q3_2025 and Q4_2025: churn_rate should increase"
                if s == 'SMB' and q in ['Q3_2025', 'Q4_2025']:
                    if q == 'Q3_2025':
                        churn_rate = 0.14
                    else:
                        churn_rate = 0.20
                        
                churned_custs = int(round(starting_custs * churn_rate))
                if churned_custs == 0 and churn_rate > 0:
                    churned_custs = 1
                    
                retention_rate = 1.0 - churn_rate
                
                rows.append({
                    'quarter': q,
                    'region': r,
                    'segment': s,
                    'churn_rate': round(churn_rate, 4),
                    'churned_customers': churned_custs,
                    'starting_customers': starting_custs,
                    'retention_rate': round(retention_rate, 4)
                })
                
    return pd.DataFrame(rows)

def generate_support_tickets(df_customers):
    # We want between 200 and 500 rows.
    # Let's generate tickets linked to our active/churned customers.
    tickets = []
    ticket_id_counter = 1
    
    # We will generate a base pool of tickets across quarters, customers, products
    # To encode the narratives:
    # 1. APAC Enterprise Q4 Support Escalations Spike
    # 3. SMB Support slow down (longer response times) in Q3/Q4 2025
    # 4. FlowOps Q4 release instability (spike in FlowOps support tickets and escalations)
    
    for q in QUARTERS:
        for _, cust in df_customers.iterrows():
            cid = cust['customer_id']
            region = cust['region']
            seg = cust['segment']
            
            # Determine base tickets count per customer per quarter
            if seg == 'Enterprise':
                base_prob = 0.35
            elif seg == 'Mid-Market':
                base_prob = 0.20
            else:
                base_prob = 0.10
                
            # Narrative multipliers/triggers
            # Narrative 1: APAC Enterprise Q4 ticket spike
            if q == 'Q4_2025' and region == 'APAC' and seg == 'Enterprise':
                base_prob = 0.85
                
            # Narrative 4: FlowOps Release ticket spike in Q4
            if q == 'Q4_2025':
                base_prob += 0.15
                
            if np.random.rand() < base_prob:
                # Let's create 1 or 2 tickets
                num_t = np.random.choice([1, 2], p=[0.7, 0.3])
                for _ in range(num_t):
                    product = np.random.choice(PRODUCTS)
                    
                    # Force product to FlowOps in Q4 for Narrative 4
                    if q == 'Q4_2025' and np.random.rand() < 0.60:
                        product = 'FlowOps'
                        
                    severity = np.random.choice(['Low', 'Medium', 'High', 'Critical'], p=[0.4, 0.4, 0.15, 0.05])
                    escalated = np.random.choice([True, False], p=[0.10, 0.90])
                    
                    # Base times
                    resp_time = np.random.uniform(0.5, 4.0)
                    res_time = np.random.uniform(4.0, 24.0)
                    
                    # Narrative 1: APAC Enterprise Support escalations increase
                    if q == 'Q4_2025' and region == 'APAC' and seg == 'Enterprise':
                        severity = np.random.choice(['High', 'Critical'], p=[0.6, 0.4])
                        escalated = True
                        resp_time = np.random.uniform(12.0, 36.0)  # Timezone coverage gap
                        res_time = np.random.uniform(36.0, 96.0)
                        
                    # Narrative 3: SMB Support response/resolution times worsen in Q3 and Q4
                    if seg == 'SMB' and q in ['Q3_2025', 'Q4_2025']:
                        resp_time = np.random.uniform(18.0, 48.0)
                        res_time = np.random.uniform(48.0, 120.0)
                        
                    # Narrative 4: FlowOps Release Side Effect (Q4 FlowOps tickets are high severity & escalated)
                    if q == 'Q4_2025' and product == 'FlowOps':
                        severity = np.random.choice(['High', 'Critical'], p=[0.7, 0.3])
                        escalated = True
                        resp_time = np.random.uniform(2.0, 10.0)
                        res_time = np.random.uniform(24.0, 72.0)
                        
                    issue_types = {
                        'InsightOS': ['UI Glitch', 'Dashboard Load Timeout', 'Export CSV Failed', 'User Access Management'],
                        'MetricHub': ['SQL Generation Error', 'Incorrect Sum Aggregation', 'Semantic Layer Sync Failed', 'Caching Stale Data'],
                        'FlowOps': ['Pipeline Execution Stalled', 'API Rate Limit Exceeded', 'v2.0 Migration Memory Leak', 'Connection Lost to Database']
                    }
                    
                    issue = np.random.choice(issue_types[product])
                    
                    tickets.append({
                        'ticket_id': f"TKT_{ticket_id_counter:04d}",
                        'customer_id': cid,
                        'quarter': q,
                        'region': region,
                        'segment': seg,
                        'product': product,
                        'issue_type': issue,
                        'severity': severity,
                        'escalated': escalated,
                        'response_time_hours': round(resp_time, 1),
                        'resolution_time_hours': round(res_time, 1)
                    })
                    ticket_id_counter += 1
                    
    df_tickets = pd.DataFrame(tickets)
    
    # Trim to stay within 200-500 rows if necessary
    if len(df_tickets) > 500:
        df_tickets = df_tickets.sample(450, random_state=42).sort_values(by=['quarter', 'ticket_id']).reset_index(drop=True)
    elif len(df_tickets) < 200:
        # Pad with some random tickets
        pass
        
    return df_tickets

def generate_product_usage():
    # Exactly 144 rows: 4 quarters × 4 regions × 3 segments × 3 products
    rows = []
    for q in QUARTERS:
        for r in REGIONS:
            for s in SEGMENTS:
                for p in PRODUCTS:
                    # Base usage metrics
                    if s == 'Enterprise':
                        active_users = int(np.random.uniform(80, 150))
                        usage_score = np.random.uniform(85, 95)
                        feature_adoption = np.random.uniform(0.70, 0.85)
                        avg_sessions = np.random.uniform(25, 45)
                    elif s == 'Mid-Market':
                        active_users = int(np.random.uniform(20, 50))
                        usage_score = np.random.uniform(75, 88)
                        feature_adoption = np.random.uniform(0.60, 0.78)
                        avg_sessions = np.random.uniform(15, 28)
                    else:  # SMB
                        active_users = int(np.random.uniform(5, 15))
                        usage_score = np.random.uniform(65, 80)
                        feature_adoption = np.random.uniform(0.40, 0.65)
                        avg_sessions = np.random.uniform(8, 18)
                        
                    # Narrative 3: SMB usage decline in Q3/Q4_2025 before/during churn
                    if s == 'SMB' and q in ['Q3_2025', 'Q4_2025']:
                        usage_score = usage_score * 0.75
                        feature_adoption = feature_adoption * 0.70
                        avg_sessions = avg_sessions * 0.68
                        
                    # Narrative 4: FlowOps Release Side Effect in Q4_2025
                    # usage_score drops, especially for Enterprise
                    if q == 'Q4_2025' and p == 'FlowOps':
                        if s == 'Enterprise':
                            usage_score = usage_score * 0.55  # Severe drop
                            feature_adoption = feature_adoption * 0.50
                            avg_sessions = avg_sessions * 0.50
                        else:
                            usage_score = usage_score * 0.80
                            feature_adoption = feature_adoption * 0.75
                            avg_sessions = avg_sessions * 0.80
                            
                    # Narrative 1: APAC Enterprise Q4 FlowOps instability or usage decline
                    if q == 'Q4_2025' and r == 'APAC' and s == 'Enterprise' and p == 'FlowOps':
                        usage_score = usage_score * 0.80  # Additional hit
                        avg_sessions = avg_sessions * 0.85
                        
                    rows.append({
                        'quarter': q,
                        'region': r,
                        'segment': s,
                        'product': p,
                        'active_users': active_users,
                        'usage_score': round(usage_score, 1),
                        'feature_adoption_rate': round(feature_adoption, 3),
                        'avg_sessions_per_account': round(avg_sessions, 1)
                    })
                    
    return pd.DataFrame(rows)

def generate_sales_pipeline():
    # Exactly 48 rows: 4 quarters × 4 regions × 3 segments
    rows = []
    for q in QUARTERS:
        for r in REGIONS:
            for s in SEGMENTS:
                # Base parameters
                if s == 'Enterprise':
                    pipe_val = 600000.0
                    opps = 15
                    win_rate = 0.22
                    conv_rate = 0.20
                    cycle_days = 90
                elif s == 'Mid-Market':
                    pipe_val = 250000.0
                    opps = 35
                    win_rate = 0.28
                    conv_rate = 0.25
                    cycle_days = 60
                else:  # SMB
                    pipe_val = 100000.0
                    opps = 80
                    win_rate = 0.32
                    conv_rate = 0.30
                    cycle_days = 30
                    
                q_idx = QUARTERS.index(q)
                growth = 1.0 + q_idx * 0.08
                pipe_val = pipe_val * growth * np.random.uniform(0.9, 1.1)
                opps = int(opps * growth * np.random.uniform(0.9, 1.1))
                
                # Narrative 2: EMEA Pipeline Illusion in Q4_2025
                # pipeline_value increases, conversion_rate drops, avg_sales_cycle_days increases
                if q == 'Q4_2025' and r == 'EMEA':
                    pipe_val = pipe_val * 1.85  # Massive spike
                    opps = int(opps * 1.45)
                    conv_rate = conv_rate * 0.35  # Severe drop (e.g. from 20% to 7%)
                    win_rate = win_rate * 0.40
                    cycle_days = int(cycle_days * 1.80)  # Long sales cycle
                else:
                    conv_rate = conv_rate * np.random.uniform(0.9, 1.1)
                    win_rate = win_rate * np.random.uniform(0.9, 1.1)
                    cycle_days = int(cycle_days * np.random.uniform(0.95, 1.05))
                    
                rows.append({
                    'quarter': q,
                    'region': r,
                    'segment': s,
                    'pipeline_value': round(pipe_val, 2),
                    'opportunities_created': opps,
                    'win_rate': round(win_rate, 3),
                    'conversion_rate': round(conv_rate, 3),
                    'avg_sales_cycle_days': cycle_days
                })
                
    return pd.DataFrame(rows)

def generate_region_targets():
    # Exactly 16 rows: 4 quarters × 4 regions
    rows = []
    for q in QUARTERS:
        for r in REGIONS:
            # Set regional targets that grow quarterly
            q_idx = QUARTERS.index(q)
            growth = 1.0 + q_idx * 0.10
            
            if r == 'North America':
                rev_target = 800000.0 * growth
                pipe_target = 2500000.0 * growth
            elif r == 'EMEA':
                rev_target = 600000.0 * growth
                pipe_target = 1800000.0 * growth
            elif r == 'APAC':
                rev_target = 400000.0 * growth
                pipe_target = 1200000.0 * growth
            else:  # LATAM
                rev_target = 200000.0 * growth
                pipe_target = 600000.0 * growth
                
            rows.append({
                'quarter': q,
                'region': r,
                'revenue_target': round(rev_target, 2),
                'pipeline_target': round(pipe_target, 2),
                'churn_target': 0.05,
                'gross_margin_target': 0.78
            })
            
    return pd.DataFrame(rows)

def main():
    print("--- STARTING SYNTHETIC DATA GENERATION ---")
    ensure_directories()
    
    # Generate datasets
    df_customers = generate_customers()
    df_subscriptions = generate_subscriptions(df_customers)
    df_revenue = generate_revenue()
    df_marketing_spend = generate_marketing_spend()
    df_churn = generate_churn()
    df_tickets = generate_support_tickets(df_customers)
    df_product_usage = generate_product_usage()
    df_sales_pipeline = generate_sales_pipeline()
    df_region_targets = generate_region_targets()
    
    # Save CSVs
    files = {
        'customers.csv': df_customers,
        'subscriptions.csv': df_subscriptions,
        'revenue.csv': df_revenue,
        'marketing_spend.csv': df_marketing_spend,
        'churn.csv': df_churn,
        'support_tickets.csv': df_tickets,
        'product_usage.csv': df_product_usage,
        'sales_pipeline.csv': df_sales_pipeline,
        'region_targets.csv': df_region_targets
    }
    
    for filename, df in files.items():
        filepath = os.path.join('data/raw/structured', filename)
        df.to_csv(filepath, index=False)
        print(f"Saved {filename}: {len(df)} rows, {len(df.columns)} columns")
        
    print("\n--- SANITY CHECKS ---")
    
    # Validate row counts and run assertions
    errors = 0
    
    # 1. revenue.csv has exactly 144 rows
    if len(df_revenue) == 144:
        print("[OK] revenue.csv: exactly 144 rows")
    else:
        print(f"[FAIL] revenue.csv: expected 144, got {len(df_revenue)}")
        errors += 1
        
    # 2. marketing_spend.csv has exactly 48 rows
    if len(df_marketing_spend) == 48:
        print("[OK] marketing_spend.csv: exactly 48 rows")
    else:
        print(f"[FAIL] marketing_spend.csv: expected 48, got {len(df_marketing_spend)}")
        errors += 1
        
    # 3. churn.csv has exactly 48 rows
    if len(df_churn) == 48:
        print("[OK] churn.csv: exactly 48 rows")
    else:
        print(f"[FAIL] churn.csv: expected 48, got {len(df_churn)}")
        errors += 1
        
    # 4. product_usage.csv has exactly 144 rows
    if len(df_product_usage) == 144:
        print("[OK] product_usage.csv: exactly 144 rows")
    else:
        print(f"[FAIL] product_usage.csv: expected 144, got {len(df_product_usage)}")
        errors += 1
        
    # 5. sales_pipeline.csv has exactly 48 rows
    if len(df_sales_pipeline) == 48:
        print("[OK] sales_pipeline.csv: exactly 48 rows")
    else:
        print(f"[FAIL] sales_pipeline.csv: expected 48, got {len(df_sales_pipeline)}")
        errors += 1
        
    # 6. region_targets.csv has exactly 16 rows
    if len(df_region_targets) == 16:
        print("[OK] region_targets.csv: exactly 16 rows")
    else:
        print(f"[FAIL] region_targets.csv: expected 16, got {len(df_region_targets)}")
        errors += 1
        
    # 7. customers.csv has between 300 and 500 rows
    if 300 <= len(df_customers) <= 500:
        print(f"[OK] customers.csv: {len(df_customers)} rows (within [300, 500])")
    else:
        print(f"[FAIL] customers.csv: expected 300-500, got {len(df_customers)}")
        errors += 1
        
    # 8. subscriptions.csv has between 300 and 500 rows
    if 300 <= len(df_subscriptions) <= 500:
        print(f"[OK] subscriptions.csv: {len(df_subscriptions)} rows (within [300, 500])")
    else:
        print(f"[FAIL] subscriptions.csv: expected 300-500, got {len(df_subscriptions)}")
        errors += 1
        
    # 9. support_tickets.csv has between 200 and 500 rows
    if 200 <= len(df_tickets) <= 500:
        print(f"[OK] support_tickets.csv: {len(df_tickets)} rows (within [200, 500])")
    else:
        print(f"[FAIL] support_tickets.csv: expected 200-500, got {len(df_tickets)}")
        errors += 1
        
    if errors == 0:
        print("\n*** ALL SANITY CHECKS PASSED SUCCESSFULLY! ***")
    else:
        print(f"\n!!! FAILED SANITY CHECKS: {errors} errors found.")
        exit(1)

if __name__ == "__main__":
    main()
