import os
from pathlib import Path
import pandas as pd

# Expected schemas mapping
SCHEMAS = {
    "revenue": [
        "quarter", "region", "segment", "product", "recognized_revenue", "bookings", "pipeline_value", "gross_margin"
    ],
    "customers": [
        "customer_id", "customer_name", "region", "segment", "industry", "signup_quarter", "status"
    ],
    "marketing_spend": [
        "quarter", "region", "channel", "spend", "campaign_name", "leads_generated"
    ],
    "churn": [
        "quarter", "region", "segment", "churn_rate", "churned_customers", "starting_customers", "retention_rate"
    ],
    "support_tickets": [
        "ticket_id", "customer_id", "quarter", "region", "segment", "product", "issue_type", "severity", "escalated", "response_time_hours", "resolution_time_hours"
    ],
    "product_usage": [
        "quarter", "region", "segment", "product", "active_users", "usage_score", "feature_adoption_rate", "avg_sessions_per_account"
    ],
    "sales_pipeline": [
        "quarter", "region", "segment", "pipeline_value", "opportunities_created", "win_rate", "conversion_rate", "avg_sales_cycle_days"
    ],
    "subscriptions": [
        "subscription_id", "customer_id", "product", "plan_type", "start_quarter", "renewal_quarter", "arr", "status"
    ],
    "region_targets": [
        "quarter", "region", "revenue_target", "pipeline_target", "churn_target", "gross_margin_target"
    ]
}

def validate_table_schema(table_name: str, df: pd.DataFrame) -> None:
    """
    Validates the schema of a given DataFrame against the expected columns.
    Raises ValueError if any required columns are missing or if the DataFrame is empty.
    """
    if table_name not in SCHEMAS:
        raise ValueError(f"Unknown table schema for: {table_name}")

    if df.empty:
        raise ValueError(f"Table '{table_name}' is empty.")

    expected_cols = SCHEMAS[table_name]
    actual_cols = list(df.columns)

    missing_cols = [col for col in expected_cols if col not in actual_cols]
    if missing_cols:
        raise ValueError(f"Table '{table_name}' is missing required columns: {missing_cols}")

def load_table(path: str | Path) -> pd.DataFrame:
    """
    Loads a single CSV file, validates its schema, and returns a pandas DataFrame.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Required CSV file missing: {path_obj}")

    # Check if empty (size check)
    if path_obj.stat().st_size == 0:
        raise ValueError(f"CSV file is empty: {path_obj}")

    try:
        df = pd.read_csv(path_obj)
    except Exception as e:
        raise ValueError(f"Failed to read CSV file {path_obj}: {e}") from e

    table_name = path_obj.stem
    validate_table_schema(table_name, df)

    return df

def load_tables(directory: str | Path) -> dict[str, pd.DataFrame]:
    """
    Loads and validates all expected CSV tables from the specified directory.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"Structured CSV input directory missing: {dir_path}")

    tables = {}
    for table_name in SCHEMAS.keys():
        csv_path = dir_path / f"{table_name}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Required CSV file missing: {csv_path}")
        tables[table_name] = load_table(csv_path)

    return tables
