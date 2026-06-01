import duckdb
from pathlib import Path
from scripts.build_duckdb import build_duckdb

FORBIDDEN_KEYWORD = "Analyst" + "Graph"

def test_duckdb_build_integration():
    db_path = Path("data/warehouse/veridian.duckdb")
    
    # 1. Run the build function
    build_duckdb()
    
    # 2. Check file is created
    assert db_path.exists(), f"DuckDB warehouse must be created at {db_path}"
    assert db_path.stat().st_size > 0, "DuckDB file must not be empty"
    
    # 3. Connect and query tables
    con = duckdb.connect(str(db_path))
    
    # Verify tables list
    tables_res = con.execute("SHOW TABLES").fetchall()
    table_names = [r[0] for r in tables_res]
    
    expected_tables = [
        "revenue", "customers", "marketing_spend", "churn", "support_tickets",
        "product_usage", "sales_pipeline", "subscriptions", "region_targets"
    ]
    
    for t in expected_tables:
        assert t in table_names, f"Table '{t}' missing from DuckDB warehouse"
        
    # 4. Check revenue count
    rev_count = con.execute("SELECT COUNT(*) FROM revenue").fetchone()[0]
    assert rev_count == 144, f"Expected exactly 144 rows in revenue, got {rev_count}"
    
    # 5. Check support tickets count
    tkt_count = con.execute("SELECT COUNT(*) FROM support_tickets").fetchone()[0]
    assert 200 <= tkt_count <= 500, f"Expected support_tickets between 200 and 500 rows, got {tkt_count}"
    
    # 6. Check a simple aggregate query works (Query 1)
    agg_res = con.execute("""
        SELECT region, SUM(recognized_revenue) AS total_revenue
        FROM revenue
        GROUP BY region
        ORDER BY region
    """).fetchall()
    assert len(agg_res) == 4, f"Expected exactly 4 regions, got {len(agg_res)}"
    for row in agg_res:
        region = row[0]
        total_revenue = row[1]
        assert region, "Expected region to be non-empty"
        assert total_revenue > 0, f"Expected total_revenue > 0 for {region}, got {total_revenue}"
        assert FORBIDDEN_KEYWORD not in str(region)

    # 7. Check business-pattern sanity query (Query 2)
    # APAC Enterprise revenue Q4_2025 should be lower than Q3_2025
    q_res = con.execute("""
        SELECT quarter, SUM(recognized_revenue) AS revenue
        FROM revenue
        WHERE region = 'APAC' AND segment = 'Enterprise'
        GROUP BY quarter
        ORDER BY quarter
    """).fetchall()
    
    q_data = {row[0]: row[1] for row in q_res}
    assert "Q3_2025" in q_data, "Q3_2025 data should exist"
    assert "Q4_2025" in q_data, "Q4_2025 data should exist"
    assert q_data["Q4_2025"] < q_data["Q3_2025"], f"APAC Enterprise Q4 revenue ({q_data['Q4_2025']}) should be lower than Q3 ({q_data['Q3_2025']})"
    
    con.close()

def test_duckdb_narrative2_emea_pipeline_illusion():
    """EMEA pipeline illusion: Q4 pipeline_value high but conversion_rate drops and cycle lengthens."""
    from scripts.build_duckdb import build_duckdb
    build_duckdb()
    db_path = Path("data/warehouse/veridian.duckdb")
    con = duckdb.connect(str(db_path))
    res = con.execute("""
        SELECT quarter,
               SUM(pipeline_value) AS pipeline_value,
               AVG(conversion_rate) AS conversion_rate,
               AVG(avg_sales_cycle_days) AS avg_sales_cycle_days
        FROM sales_pipeline
        WHERE region = 'EMEA'
        GROUP BY quarter
        ORDER BY quarter
    """).fetchall()
    assert len(res) == 4, f"Expected 4 quarters of EMEA pipeline data, got {len(res)}"
    quarters = [r[0] for r in res]
    q_data = {r[0]: {"pipeline_value": r[1], "conversion_rate": r[2], "avg_sales_cycle_days": r[3]} for r in res}
    # Q4 conversion_rate drops vs Q3 (pipeline illusion: high pipeline, low conversion)
    assert q_data[quarters[-1]]["conversion_rate"] < q_data[quarters[-2]]["conversion_rate"], \
        "EMEA Q4 conversion_rate should drop (pipeline illusion narrative)"
    con.close()


def test_duckdb_narrative3_smb_churn_increase():
    """SMB churn rate increases in later quarters (support slowdown narrative)."""
    from scripts.build_duckdb import build_duckdb
    build_duckdb()
    db_path = Path("data/warehouse/veridian.duckdb")
    con = duckdb.connect(str(db_path))
    res = con.execute("""
        SELECT quarter, churn_rate
        FROM churn
        WHERE region = 'North America' AND segment = 'SMB'
        ORDER BY quarter
    """).fetchall()
    assert len(res) >= 2, f"Expected at least 2 quarters of SMB churn data, got {len(res)}"
    quarters = [r[0] for r in res]
    q_data = {r[0]: r[1] for r in res}
    assert q_data[quarters[-1]] > q_data[quarters[-2]], \
        "SMB churn_rate should increase in later quarters (support slowdown narrative)"
    con.close()


def test_duckdb_narrative4_flowops_usage_drop():
    """FlowOps Enterprise usage score drops in Q4 (release side-effect narrative)."""
    from scripts.build_duckdb import build_duckdb
    build_duckdb()
    db_path = Path("data/warehouse/veridian.duckdb")
    con = duckdb.connect(str(db_path))
    res = con.execute("""
        SELECT quarter,
               AVG(usage_score) AS usage_score,
               SUM(active_users) AS active_users,
               AVG(feature_adoption_rate) AS feature_adoption_rate
        FROM product_usage
        WHERE product = 'FlowOps' AND segment = 'Enterprise'
        GROUP BY quarter
        ORDER BY quarter
    """).fetchall()
    assert len(res) == 4, f"Expected 4 quarters of FlowOps Enterprise data, got {len(res)}"
    quarters = [r[0] for r in res]
    q_data = {r[0]: {"usage_score": r[1], "active_users": r[2], "feature_adoption_rate": r[3]} for r in res}
    # Q4 usage_score drops from Q3
    assert q_data[quarters[-1]]["usage_score"] < q_data[quarters[-2]]["usage_score"], \
        "FlowOps Enterprise Q4 usage_score should drop (release side-effect narrative)"
    con.close()


def test_duckdb_cross_table_join():
    """Revenue-customers JOIN should work across the warehouse."""
    from scripts.build_duckdb import build_duckdb
    build_duckdb()
    db_path = Path("data/warehouse/veridian.duckdb")
    con = duckdb.connect(str(db_path))
    res = con.execute("""
        SELECT r.quarter, r.region, r.segment, r.recognized_revenue
        FROM revenue r
        JOIN customers c ON r.region = c.region AND r.segment = c.segment
        LIMIT 5
    """).fetchall()
    assert len(res) > 0, "Cross-table JOIN should return at least 1 row"
    con.close()


def test_table_profiling_integration():
    import json
    from scripts.profile_tables import profile_tables
    
    profile_path = Path("data/processed/table_profiles.json")
    
    # Run the profiling script
    profile_tables()
    
    # Verify the profile json file exists
    assert profile_path.exists(), "table_profiles.json was not created"
    
    with open(profile_path, "r", encoding="utf-8") as f:
        profiles = json.load(f)
        
    expected_tables = {
        "revenue", "customers", "marketing_spend", "churn", "support_tickets",
        "product_usage", "sales_pipeline", "subscriptions", "region_targets"
    }
    
    profiled_tables = [p["table_name"] for p in profiles]
    assert len(profiled_tables) == 9
    
    for profile in profiles:
        tname = profile["table_name"]
        assert tname in expected_tables, f"Unknown profiled table: {tname}"
        
        # Verify required keys
        required_keys = [
            "table_name", "row_count", "column_count", "columns",
            "numeric_columns", "categorical_columns", "missing_values", "sample_rows"
        ]
        for key in required_keys:
            assert key in profile, f"Missing key '{key}' in profile for table '{tname}'"
            
        # Assert type and value bounds
        assert profile["row_count"] > 0, f"Row count for {tname} should be greater than 0"
        assert profile["column_count"] > 0, f"Column count for {tname} should be greater than 0"
        assert isinstance(profile["columns"], list), f"Expected columns list in {tname}"
        assert len(profile["columns"]) > 0, f"Expected non-empty columns list in {tname}"
        assert isinstance(profile["missing_values"], dict), f"Expected missing_values dict in {tname}"
        assert isinstance(profile["sample_rows"], list), f"Expected sample_rows list in {tname}"
        assert len(profile["sample_rows"]) <= 3, f"Expected at most 3 sample rows in {tname}, got {len(profile['sample_rows'])}"
