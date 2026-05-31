import json
import sys
from pathlib import Path
from typing import Any

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


STRUCTURED_DIR = Path("data/raw/structured")
UNSTRUCTURED_DIR = Path("data/raw/unstructured")
PROCESSED_DIR = Path("data/processed")
WAREHOUSE_PATH = Path("data/warehouse/veridian.duckdb")
BENCHMARK_PATH = Path("benchmarks/enterpriseqa_v0.jsonl")

REQUIRED_CSVS = [
    "revenue.csv",
    "customers.csv",
    "marketing_spend.csv",
    "churn.csv",
    "support_tickets.csv",
    "product_usage.csv",
    "sales_pipeline.csv",
    "subscriptions.csv",
    "region_targets.csv",
]
REQUIRED_TABLES = {name.removesuffix(".csv") for name in REQUIRED_CSVS}

REQUIRED_DOCS = [
    "kpi_definitions.md",
    "schema_definitions.md",
    "regional_taxonomy.md",
    "q1_business_review.md",
    "q2_business_review.md",
    "q3_business_review.md",
    "q4_business_review.md",
    "q4_apac_revenue_report.md",
    "pricing_change_memo.md",
    "marketing_campaign_memo.md",
    "support_escalation_report.md",
    "product_release_notes.md",
    "customer_success_notes.md",
    "emea_pipeline_review.md",
    "smb_churn_review.md",
    "enterprise_retention_notes.md",
    "flowops_release_incident.md",
    "sales_cycle_review.md",
    "customer_segment_guide.md",
    "known_metric_confusions.md",
]

REQUIRED_PROCESSED = [
    "document_chunks.jsonl",
    "document_metadata.jsonl",
    "table_profiles.json",
    "schema_snapshot.json",
]

EXPECTED_REGIONS = {"APAC", "EMEA", "North America", "LATAM", "Global"}
EXPECTED_SEGMENTS = {"SMB", "Mid-Market", "Enterprise", "All"}
BANNED_KEYWORD = "Analyst" + "Graph"


class ValidationGate:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def check(self, name: str, condition: bool, detail: str = "") -> None:
        if condition:
            print(f"[PASS] {name}")
            return
        message = f"{name}: {detail}" if detail else name
        print(f"[FAIL] {message}")
        self.failures.append(message)

    def require(self, name: str, condition: bool, detail: str = "") -> None:
        self.check(name, condition, detail)
        if not condition:
            raise AssertionError(f"{name}: {detail}")


def load_jsonl(path: Path, required_fields: list[str], gate: ValidationGate) -> list[dict[str, Any]]:
    gate.require(f"{path} exists", path.exists(), "file is missing")
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise AssertionError(f"{path} contains empty line {line_number}")
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{path} line {line_number} is invalid JSON: {exc}") from exc
        missing = [field for field in required_fields if field not in record]
        if missing:
            raise AssertionError(f"{path} line {line_number} missing required fields: {missing}")
        records.append(record)
    gate.check(f"{path} is valid JSONL with no empty lines", True)
    gate.check(f"{path} records contain required fields", True)
    return records


def normalize_expected_doc(value: str) -> str:
    path = Path(value)
    name = path.name
    return name if name.endswith(".md") else f"{name}.md"


def collect_metric_text(snapshot: dict[str, Any]) -> str:
    metric_sources = [
        Path("docs/schema_definitions.md"),
        Path("docs/week2_study_notes.md"),
        PROCESSED_DIR / "schema_snapshot.json",
    ]
    text = json.dumps(snapshot, sort_keys=True)
    for path in metric_sources:
        if path.exists():
            text += "\n" + path.read_text(encoding="utf-8")
    return text.lower()


def validate_required_files(gate: ValidationGate) -> None:
    missing_csvs = [name for name in REQUIRED_CSVS if not (STRUCTURED_DIR / name).exists()]
    gate.check("Required structured CSV files exist", not missing_csvs, f"missing {missing_csvs}")

    missing_docs = [name for name in REQUIRED_DOCS if not (UNSTRUCTURED_DIR / name).exists()]
    gate.check("Required unstructured markdown docs exist", not missing_docs, f"missing {missing_docs}")

    missing_processed = [name for name in REQUIRED_PROCESSED if not (PROCESSED_DIR / name).exists()]
    gate.check("Required processed files exist", not missing_processed, f"missing {missing_processed}")

    gate.check(
        "DuckDB database exists",
        WAREHOUSE_PATH.exists() and WAREHOUSE_PATH.stat().st_size > 0,
        f"missing or empty: {WAREHOUSE_PATH}",
    )


def validate_loaders(gate: ValidationGate) -> None:
    from app.ingestion.document_loader import load_documents
    from app.ingestion.table_loader import load_tables

    tables = load_tables(STRUCTURED_DIR)
    gate.check("CSVs load through table_loader.load_tables", set(tables) == REQUIRED_TABLES, f"loaded {sorted(tables)}")

    documents = load_documents(UNSTRUCTURED_DIR)
    gate.check("Markdown docs load through document_loader.load_documents", len(documents) == 20, f"loaded {len(documents)}")


def validate_chunks(gate: ValidationGate) -> list[dict[str, Any]]:
    required = ["chunk_id", "doc_id", "title", "doc_type", "text", "chunk_index", "metadata", "source_path"]
    chunks = load_jsonl(PROCESSED_DIR / "document_chunks.jsonl", required, gate)

    chunk_ids = [chunk["chunk_id"] for chunk in chunks]
    gate.check("document_chunks.jsonl chunk_id values are unique", len(chunk_ids) == len(set(chunk_ids)))

    raw_root = (Path.cwd() / UNSTRUCTURED_DIR).resolve()
    chunks_have_text = True
    chunks_have_source_path = True
    chunks_under_raw = True
    chunks_have_related_metrics = True
    for chunk in chunks:
        chunks_have_text = chunks_have_text and bool(str(chunk["text"]).strip())

        source_path = Path(chunk["source_path"])
        source_resolved = source_path if source_path.is_absolute() else Path.cwd() / source_path
        try:
            inside_raw = source_resolved.resolve().is_relative_to(raw_root)
        except FileNotFoundError:
            inside_raw = str(source_resolved).replace("\\", "/").endswith(str(source_path).replace("\\", "/"))

        chunks_have_source_path = chunks_have_source_path and bool(str(source_path)) and source_path.suffix == ".md"
        chunks_under_raw = chunks_under_raw and inside_raw

        metadata = chunk["metadata"]
        related_metrics = metadata.get("related_metrics") if isinstance(metadata, dict) else None
        chunks_have_related_metrics = chunks_have_related_metrics and isinstance(related_metrics, list) and bool(related_metrics)
    gate.check("All chunks have non-empty text", chunks_have_text)
    gate.check("All chunks preserve non-empty markdown source_path", chunks_have_source_path)
    gate.check("All chunk source_path values are under data/raw/unstructured", chunks_under_raw)
    gate.check("All chunks have non-empty metadata.related_metrics", chunks_have_related_metrics)
    return chunks


def validate_metadata(gate: ValidationGate) -> list[dict[str, Any]]:
    required = ["doc_id", "title", "doc_type", "quarter", "region", "segment", "related_metrics", "source", "source_path"]
    metadata = load_jsonl(PROCESSED_DIR / "document_metadata.jsonl", required, gate)
    gate.check("document_metadata.jsonl has exactly 20 records", len(metadata) == 20, f"got {len(metadata)}")
    return metadata


def validate_table_profiles(gate: ValidationGate) -> list[dict[str, Any]]:
    path = PROCESSED_DIR / "table_profiles.json"
    profiles = json.loads(path.read_text(encoding="utf-8"))
    required_keys = {
        "table_name",
        "row_count",
        "column_count",
        "columns",
        "numeric_columns",
        "categorical_columns",
        "missing_values",
        "sample_rows",
    }

    profile_tables = {profile.get("table_name") for profile in profiles}
    gate.check("table_profiles.json contains all 9 expected tables", profile_tables == REQUIRED_TABLES, f"got {sorted(profile_tables)}")

    for profile in profiles:
        table_name = profile.get("table_name", "<missing>")
        missing = required_keys - set(profile)
        gate.check(f"Profile {table_name} has required keys", not missing, f"missing {sorted(missing)}")
        gate.check(f"Profile {table_name} row_count > 0", profile.get("row_count", 0) > 0)
        gate.check(f"Profile {table_name} column_count > 0", profile.get("column_count", 0) > 0)
        gate.check(f"Profile {table_name} columns non-empty", bool(profile.get("columns")))
        gate.check(f"Profile {table_name} sample_rows has at most 3 rows", len(profile.get("sample_rows", [])) <= 3)
    return profiles


def validate_schema_snapshot(gate: ValidationGate) -> dict[str, Any]:
    path = PROCESSED_DIR / "schema_snapshot.json"
    snapshot = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "number_of_documents",
        "number_of_chunks",
        "document_types",
        "quarters",
        "regions",
        "segments",
        "related_metrics",
        "source_files",
        "generated_at",
    }
    missing = required - set(snapshot)
    gate.check("schema_snapshot.json has required keys", not missing, f"missing {sorted(missing)}")
    gate.check("schema_snapshot.json number_of_documents >= 20", snapshot.get("number_of_documents", 0) >= 20)
    gate.check("schema_snapshot.json number_of_chunks >= 20", snapshot.get("number_of_chunks", 0) >= 20)
    gate.check("schema_snapshot.json contains expected regions", EXPECTED_REGIONS <= set(snapshot.get("regions", {})))
    gate.check("schema_snapshot.json contains expected segments", EXPECTED_SEGMENTS <= set(snapshot.get("segments", {})))
    return snapshot


def validate_duckdb(gate: ValidationGate) -> list[str]:
    con = duckdb.connect(str(WAREHOUSE_PATH), read_only=True)
    try:
        table_names = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
        gate.check("DuckDB contains all 9 expected tables", REQUIRED_TABLES <= table_names, f"missing {sorted(REQUIRED_TABLES - table_names)}")

        revenue_count = con.execute("SELECT COUNT(*) FROM revenue").fetchone()[0]
        gate.check("DuckDB revenue row count is 144", revenue_count == 144, f"got {revenue_count}")

        support_count = con.execute("SELECT COUNT(*) FROM support_tickets").fetchone()[0]
        gate.check("DuckDB support_tickets row count is between 200 and 500", 200 <= support_count <= 500, f"got {support_count}")

        aggregate_rows = con.execute(
            """
            SELECT region, SUM(recognized_revenue) AS total_revenue
            FROM revenue
            GROUP BY region
            """
        ).fetchall()
        gate.check("DuckDB revenue aggregation returns rows", bool(aggregate_rows))

        q_rows = con.execute(
            """
            SELECT quarter, SUM(recognized_revenue) AS revenue
            FROM revenue
            WHERE region = 'APAC' AND segment = 'Enterprise'
            GROUP BY quarter
            ORDER BY quarter
            """
        ).fetchall()
        q_data = {quarter: revenue for quarter, revenue in q_rows}
        gate.check(
            "DuckDB APAC Enterprise Q4 revenue is lower than Q3",
            q_data.get("Q4_2025", 0) < q_data.get("Q3_2025", 0),
            f"Q3={q_data.get('Q3_2025')}, Q4={q_data.get('Q4_2025')}",
        )
        return sorted(table_names)
    finally:
        con.close()


def validate_benchmark(gate: ValidationGate, snapshot: dict[str, Any]) -> None:
    if not BENCHMARK_PATH.exists():
        print("[PASS] benchmarks/enterpriseqa_v0.jsonl absent, benchmark alignment skipped")
        return

    metric_text = collect_metric_text(snapshot)
    valid_doc_files = {path.name for path in UNSTRUCTURED_DIR.glob("*.md")}

    for line_number, line in enumerate(BENCHMARK_PATH.read_text(encoding="utf-8").splitlines(), 1):
        gate.check(f"Benchmark line {line_number} is non-empty", bool(line.strip()))
        item = json.loads(line)
        gate.check(f"Benchmark line {line_number} question is non-empty", bool(str(item.get("question", "")).strip()))

        for doc in item.get("expected_docs", []) or []:
            doc_file = normalize_expected_doc(str(doc))
            gate.check(f"Benchmark line {line_number} expected_doc exists: {doc}", doc_file in valid_doc_files)

        for table in item.get("expected_tables", []) or []:
            table_name = Path(str(table)).stem
            gate.check(f"Benchmark line {line_number} expected_table exists: {table}", table_name in REQUIRED_TABLES)

        for metric in item.get("expected_metrics", []) or []:
            metric_key = str(metric).lower()
            gate.check(f"Benchmark line {line_number} expected_metric is documented: {metric}", metric_key in metric_text)


def validate_banned_keyword(gate: ValidationGate) -> None:
    roots = [
        Path("docs"),
        Path("app/ingestion"),
        Path("scripts"),
        Path("tests"),
        UNSTRUCTURED_DIR,
        Path("benchmarks"),
    ]
    banned_hits: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix in {".pyc", ".duckdb", ".db"} or "__pycache__" in path.parts:
                continue
            try:
                if BANNED_KEYWORD in path.read_text(encoding="utf-8"):
                    banned_hits.append(str(path))
            except UnicodeDecodeError:
                continue
    gate.check(f"Banned keyword check: no {BANNED_KEYWORD}", not banned_hits, f"found in {banned_hits}")


def run_validation() -> None:
    print("==================================================")
    print("          STARTING WEEK 2 VALIDATION GATE")
    print("==================================================")

    gate = ValidationGate()
    validate_required_files(gate)
    validate_loaders(gate)
    validate_chunks(gate)
    validate_metadata(gate)
    validate_table_profiles(gate)
    snapshot = validate_schema_snapshot(gate)
    validate_duckdb(gate)
    validate_benchmark(gate, snapshot)
    validate_banned_keyword(gate)

    print("==================================================")
    if gate.failures:
        print("!!! WEEK 2 VALIDATION FAILED !!!")
        for failure in gate.failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("*** WEEK 2 VALIDATION PASSED ***")
    print("==================================================")


if __name__ == "__main__":
    try:
        run_validation()
    except AssertionError as exc:
        print(f"[FAIL] {exc}")
        sys.exit(1)
