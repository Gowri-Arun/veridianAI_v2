import pytest
import pandas as pd
from pathlib import Path
from app.ingestion.table_loader import load_table, load_tables, validate_table_schema

FORBIDDEN_KEYWORD = "Analyst" + "Graph"

def test_load_table_revenue_success():
    csv_path = Path("data/raw/structured/revenue.csv")
    assert csv_path.exists(), "revenue.csv must exist in data/raw/structured"
    
    df = load_table(csv_path)
    assert not df.empty
    assert len(df) == 144
    assert list(df.columns) == [
        "quarter", "region", "segment", "product", "recognized_revenue", "bookings", "pipeline_value", "gross_margin"
    ]

def test_load_tables_all_success():
    input_dir = Path("data/raw/structured")
    assert input_dir.exists(), "Structured CSV data directory must exist"
    
    tables = load_tables(input_dir)
    assert len(tables) == 9
    
    # Assert every returned value is a pandas DataFrame, has at least 1 row, and has expected columns
    for tname, df in tables.items():
        assert isinstance(df, pd.DataFrame), f"Expected table {tname} to be a pandas DataFrame"
        assert len(df) >= 1, f"Expected table {tname} to have at least 1 row"
        
        # Verify the restricted legacy project name is nowhere in keys, columns, or cell values
        assert FORBIDDEN_KEYWORD not in tname, f"Forbidden legacy keyword in table name: {tname}"
        for col in df.columns:
            assert FORBIDDEN_KEYWORD not in col, f"Forbidden legacy keyword in column name: {col}"
            
            # Check cell values if they are string types
            if df[col].dtype == object:
                for idx, val in df[col].dropna().items():
                    assert FORBIDDEN_KEYWORD not in str(val), f"Forbidden legacy keyword in cell value of table {tname}, column {col}"

    assert "revenue" in tables
    assert len(tables["revenue"]) == 144
    
    assert "customers" in tables
    assert 300 <= len(tables["customers"]) <= 500
    
    assert "support_tickets" in tables
    assert 200 <= len(tables["support_tickets"]) <= 500

def test_validate_table_schema_valid():
    # Construct a valid revenue DataFrame manually or load it
    df = pd.read_csv("data/raw/structured/revenue.csv")
    # Should not raise exception
    validate_table_schema("revenue", df)

def test_validate_table_schema_missing_columns():
    # Create invalid DataFrame missing gross_margin
    df_invalid = pd.DataFrame({
        "quarter": ["Q1_2025"],
        "region": ["APAC"],
        "segment": ["Enterprise"],
        "product": ["InsightOS"],
        "recognized_revenue": [10000.0],
        "bookings": [12000.0],
        "pipeline_value": [30000.0]
        # missing gross_margin
    })
    # Assert the missing column name 'gross_margin' is in the error message
    with pytest.raises(ValueError, match="gross_margin"):
        validate_table_schema("revenue", df_invalid)

def test_validate_table_schema_unknown_table():
    df = pd.DataFrame({"col": [1]})
    with pytest.raises(ValueError, match="Unknown table schema"):
        validate_table_schema("unknown_table", df)

def test_load_table_rejects_empty_csv(tmp_path):
    # Empty CSV (size zero)
    empty_csv = tmp_path / "revenue.csv"
    empty_csv.write_text("")
    
    with pytest.raises(ValueError, match="CSV file is empty"):
        load_table(empty_csv)
        
    # Header only but no data rows (Pandas empty dataframe)
    header_only_csv = tmp_path / "customers.csv"
    header_only_csv.write_text("customer_id,customer_name,region,segment,industry,signup_quarter,status\n")
    
    with pytest.raises(ValueError, match="is empty"):
        load_table(header_only_csv)

def test_load_tables_missing_csv(tmp_path):
    # Copy only revenue.csv to a temp dir and try to load_tables (should fail for missing customers.csv)
    revenue_src = Path("data/raw/structured/revenue.csv")
    revenue_dest = tmp_path / "revenue.csv"
    revenue_dest.write_text(revenue_src.read_text(), encoding="utf-8")
    
    # Try to load all tables from tmp_path, should raise FileNotFoundError mentioning customers (or whichever is next required file)
    with pytest.raises(FileNotFoundError, match="customers.csv|missing"):
        load_tables(tmp_path)


def test_load_table_rejects_directory(tmp_path):
    """Passing a directory path to load_table should raise an error.
    On Windows directories have st_size == 0, so the empty-CSV check triggers."""
    with pytest.raises((IsADirectoryError, PermissionError, ValueError)):
        load_table(tmp_path)


def test_load_table_rejects_wrong_csv_content(tmp_path):
    """A CSV with completely wrong columns should be rejected
    by validate_table_schema."""
    csv_path = tmp_path / "revenue.csv"
    csv_path.write_text("a,b,c\n1,2,3\n")
    with pytest.raises(ValueError, match="missing required columns"):
        load_table(csv_path)


def test_validate_table_schema_all_tables():
    """validate_table_schema should accept valid DataFrames for all 9 known tables."""
    from app.ingestion.table_loader import SCHEMAS
    for table_name, cols in SCHEMAS.items():
        df = pd.DataFrame({col: ["dummy"] for col in cols})
        validate_table_schema(table_name, df)


def test_load_table_string_and_path():
    """load_table should accept both string and Path arguments, returning identical DataFrames."""
    csv_path = Path("data/raw/structured/revenue.csv")
    df1 = load_table(str(csv_path))
    df2 = load_table(csv_path)
    assert len(df1) == len(df2)
    assert list(df1.columns) == list(df2.columns)


def test_load_tables_all_have_required_columns_explicit():
    """Every loaded table should have all its required schema columns explicitly verified."""
    from app.ingestion.table_loader import SCHEMAS
    tables = load_tables(Path("data/raw/structured"))
    for table_name, df in tables.items():
        expected_cols = SCHEMAS[table_name]
        actual_cols = list(df.columns)
        for col in expected_cols:
            assert col in actual_cols, f"Missing column '{col}' in table '{table_name}'"
