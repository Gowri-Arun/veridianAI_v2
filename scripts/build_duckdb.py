import duckdb
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingestion.table_loader import load_tables

def build_duckdb():
    print("--- STARTING DUCKDB WAREHOUSE BUILD ---")
    
    input_dir = Path("data/raw/structured")
    warehouse_dir = Path("data/warehouse")
    warehouse_dir.mkdir(parents=True, exist_ok=True)
    
    db_path = warehouse_dir / "veridian.duckdb"
    
    # Overwrite if exists by removing file first
    if db_path.exists():
        try:
            db_path.unlink()
            print(f"Removed existing warehouse database at {db_path}")
        except Exception as e:
            print(f"Warning: could not delete existing DB file: {e}")
            
    # Connect (will create the file)
    con = duckdb.connect(str(db_path))
    
    # Load all tables using our pandas table loader
    tables = load_tables(input_dir)
    
    for table_name, df in tables.items():
        # Clean existing table just in case
        con.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        # Load DataFrame into DuckDB
        # DuckDB can register pandas DataFrames directly and query them
        con.register('df_temp', df)
        con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df_temp")
        con.unregister('df_temp')
        
        # Verify table exists and query count
        res = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
        row_count = res[0]
        
        print(f"Created table: {table_name:<20} | Loaded: {row_count:<5} rows")
        
    con.close()
    print(f"\nSuccessfully built DuckDB warehouse at: {db_path}")
    print("--- DUCKDB WAREHOUSE BUILD COMPLETE ---")

def main():
    build_duckdb()

if __name__ == "__main__":
    main()
