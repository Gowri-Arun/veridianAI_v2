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
