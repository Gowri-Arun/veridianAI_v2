import os
import json
import sys
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingestion.table_loader import load_tables

def clean_value(val):
    """Convert numpy or pandas types to clean JSON-safe Python native types."""
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer, np.int64, np.int32)):
        return int(val)
    if isinstance(val, (np.floating, np.float64, np.float32)):
        return float(val)
    if isinstance(val, np.bool_):
        return bool(val)
    return val

def profile_tables():
    print("--- STARTING TABLE PROFILING ---")
    
    input_dir = Path("data/raw/structured")
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load all tables
    tables = load_tables(input_dir)
    
    profiles = []
    
    for table_name, df in tables.items():
        # Identify columns
        columns = list(df.columns)
        
        # Identify numeric columns
        numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
        # Categorical / non-numeric columns
        categorical_cols = list(df.select_dtypes(exclude=[np.number]).columns)
        
        # Calculate missing values
        missing_vals = df.isnull().sum().to_dict()
        missing_vals_cleaned = {k: int(v) for k, v in missing_vals.items()}
        
        # Get sample rows up to 3
        sample_df = df.head(3)
        sample_rows = []
        for _, row in sample_df.iterrows():
            row_dict = {col: clean_value(val) for col, val in row.to_dict().items()}
            sample_rows.append(row_dict)
            
        profile = {
            "table_name": table_name,
            "row_count": int(len(df)),
            "column_count": int(len(columns)),
            "columns": columns,
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "missing_values": missing_vals_cleaned,
            "sample_rows": sample_rows
        }
        profiles.append(profile)
        
        # Print short summary
        print(f"Table: {table_name:<20} | Rows: {len(df):<5} | Columns: {len(columns)}")
        
    output_path = output_dir / "table_profiles.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)
        
    print(f"\nSaved profiles to {output_path}")
    print("--- TABLE PROFILING COMPLETE ---")

def main():
    profile_tables()

if __name__ == "__main__":
    main()
