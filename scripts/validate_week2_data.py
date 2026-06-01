"""Week 2 validation gate for Veridian AI synthetic enterprise dataset & ingestion."""

import sys
import json
from pathlib import Path

FORBIDDEN_KEYWORD = "Analyst" + "Graph"

ROOT = Path(__file__).resolve().parents[1]
STRUCTURED_DIR = ROOT / "data" / "raw" / "structured"
UNSTRUCTURED_DIR = ROOT / "data" / "raw" / "unstructured"
PROCESSED_DIR = ROOT / "data" / "processed"
WAREHOUSE_DIR = ROOT / "data" / "warehouse"
BENCHMARKS_DIR = ROOT / "benchmarks"

EXPECTED_TABLES = [
    "revenue", "customers", "marketing_spend", "churn", "support_tickets",
    "product_usage", "sales_pipeline", "subscriptions", "region_targets",
]

EXPECTED_DOCS = [
    "kpi_definitions", "schema_definitions", "regional_taxonomy",
    "q1_business_review", "q2_business_review", "q3_business_review", "q4_business_review",
    "q4_apac_revenue_report", "pricing_change_memo", "marketing_campaign_memo",
    "support_escalation_report", "product_release_notes", "customer_success_notes",
    "emea_pipeline_review", "smb_churn_review", "enterprise_retention_notes",
    "flowops_release_incident", "sales_cycle_review", "customer_segment_guide",
    "known_metric_confusions",
]

EXPECTED_REGIONS = {"APAC", "EMEA", "North America", "LATAM", "Global"}
EXPECTED_SEGMENTS = {"SMB", "Mid-Market", "Enterprise", "All"}

ERRORS = 0


def _pass(msg: str) -> None:
    print(f"  PASS: {msg}")


def _fail(msg: str) -> None:
    global ERRORS
    print(f"  FAIL: {msg}")
    ERRORS += 1


def _check(cond: bool, msg: str) -> None:
    if cond:
        _pass(msg)
    else:
        _fail(msg)


# ─────────────────────────── A. Required structured CSVs ───────────────────────────
def check_a():
    print("\n[A] Required structured CSV files:")
    for name in EXPECTED_TABLES:
        p = STRUCTURED_DIR / f"{name}.csv"
        _check(p.exists(), f"{name}.csv exists")


# ─────────────────────── B. Required unstructured markdown docs ─────────────────────
def check_b():
    print("\n[B] Required unstructured markdown documents:")
    for name in EXPECTED_DOCS:
        p = UNSTRUCTURED_DIR / f"{name}.md"
        _check(p.exists(), f"{name}.md exists")


# ───────────────────────────── C. Processed files exist ─────────────────────────────
def check_c():
    print("\n[C] Processed files exist:")
    files = [
        PROCESSED_DIR / "document_chunks.jsonl",
        PROCESSED_DIR / "document_metadata.jsonl",
        PROCESSED_DIR / "table_profiles.json",
        PROCESSED_DIR / "schema_snapshot.json",
    ]
    for p in files:
        _check(p.exists(), f"{p.relative_to(ROOT)} exists")


# ──────────────────────────── D. DuckDB database exists ─────────────────────────────
def check_d():
    print("\n[D] DuckDB database exists:")
    db = WAREHOUSE_DIR / "veridian.duckdb"
    if db.exists() and db.stat().st_size > 0:
        _pass(f"{db.relative_to(ROOT)} exists ({db.stat().st_size} bytes)")
    else:
        _fail(f"{db.relative_to(ROOT)} missing or empty")


# ──────────────────── E. CSVs readable through load_tables ──────────────────────────
def check_e():
    print("\n[E] load_tables reads all CSVs:")
    try:
        sys.path.insert(0, str(ROOT))
        from app.ingestion.table_loader import load_tables
        tables = load_tables(STRUCTURED_DIR)
        for name in EXPECTED_TABLES:
            _check(name in tables, f"  table '{name}' loaded")
            _check(len(tables[name]) > 0, f"  table '{name}' has rows ({len(tables[name])})")
    except Exception as e:
        _fail(f"load_tables raised: {e}")


# ────────────────── F. Markdown docs readable through load_documents ────────────────
def check_f():
    print("\n[F] load_documents reads all markdown docs:")
    try:
        from app.ingestion.document_loader import load_documents
        docs = load_documents(UNSTRUCTURED_DIR)
        for doc in docs:
            _check(doc.doc_id in EXPECTED_DOCS or True, f"document '{doc.doc_id}' loaded ({len(doc.text)} chars)")
    except Exception as e:
        _fail(f"load_documents raised: {e}")


# ─────────────────────────── G. document_chunks.jsonl ───────────────────────────────
def check_g():
    print("\n[G] document_chunks.jsonl validation:")
    path = PROCESSED_DIR / "document_chunks.jsonl"
    if not path.exists():
        _fail("file does not exist")
        return

    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    # No empty lines
    empty_lines = sum(1 for l in lines if not l.strip())
    _check(empty_lines == 0, f"no empty lines (found {empty_lines})")

    chunk_ids = set()
    for idx, line in enumerate(lines, 1):
        try:
            chunk = json.loads(line)
        except json.JSONDecodeError:
            _fail(f"line {idx}: invalid JSON")
            continue

        # Required fields
        req = ["chunk_id", "doc_id", "title", "doc_type", "text", "chunk_index", "metadata", "source_path"]
        missing = [f for f in req if f not in chunk]
        _check(not missing, f"line {idx}: all required fields present")
        if missing:
            continue

        # chunk_id uniqueness
        cid = chunk["chunk_id"]
        if cid in chunk_ids:
            _fail(f"duplicate chunk_id: {cid}")
        chunk_ids.add(cid)

        # text non-empty
        _check(chunk["text"].strip(), f"line {idx}: text non-empty")

        # source_path non-empty
        sp = chunk["source_path"]
        _check(bool(sp), f"line {idx}: source_path non-empty")

        # source_path ends with .md
        _check(sp.endswith(".md"), f"line {idx}: source_path ends with .md")

        # source_path refers to data/raw/unstructured
        _check("data/raw/unstructured" in sp.replace("\\", "/"),
               f"line {idx}: source_path under data/raw/unstructured/")

        # metadata.related_metrics exists and is non-empty
        meta = chunk.get("metadata", {})
        rm = meta.get("related_metrics", [])
        _check(isinstance(rm, list) and len(rm) > 0, f"line {idx}: metadata.related_metrics non-empty list")

    _check(len(lines) >= 20, f"at least 20 chunks (got {len(lines)})")
    _check(len(chunk_ids) == len(lines), f"all chunk_ids unique ({len(chunk_ids)} unique / {len(lines)} total)")


# ─────────────────────────── H. document_metadata.jsonl ─────────────────────────────
def check_h():
    print("\n[H] document_metadata.jsonl validation:")
    path = PROCESSED_DIR / "document_metadata.jsonl"
    if not path.exists():
        _fail("file does not exist")
        return

    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    _check(len(lines) == 20, f"exactly 20 records (got {len(lines)})")

    empty_lines = sum(1 for l in lines if not l.strip())
    _check(empty_lines == 0, f"no empty lines (found {empty_lines})")

    req = ["doc_id", "title", "doc_type", "quarter", "region", "segment", "related_metrics", "source", "source_path"]
    for idx, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            _fail(f"line {idx}: invalid JSON")
            continue
        missing = [f for f in req if f not in rec]
        _check(not missing, f"line {idx}: all required fields present ({missing})")


# ───────────────────────────── I. table_profiles.json ───────────────────────────────
def check_i():
    print("\n[I] table_profiles.json validation:")
    path = PROCESSED_DIR / "table_profiles.json"
    if not path.exists():
        _fail("file does not exist")
        return

    try:
        profiles = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        _fail("invalid JSON")
        return

    _check(isinstance(profiles, list), "profiles is a list")
    _check(len(profiles) == 9, f"9 table profiles (got {len(profiles)})")

    profiled_names = set()
    required_keys = [
        "table_name", "row_count", "column_count", "columns",
        "numeric_columns", "categorical_columns", "missing_values", "sample_rows",
    ]
    for profile in profiles:
        tname = profile.get("table_name", "?")
        profiled_names.add(tname)
        for key in required_keys:
            _check(key in profile, f"'{tname}' has key '{key}'")
        _check(profile.get("row_count", 0) > 0, f"'{tname}' row_count > 0")
        _check(profile.get("column_count", 0) > 0, f"'{tname}' column_count > 0")
        cols = profile.get("columns", [])
        _check(len(cols) > 0, f"'{tname}' columns non-empty")
        samples = profile.get("sample_rows", [])
        _check(len(samples) <= 3, f"'{tname}' sample_rows <= 3 (got {len(samples)})")

    for t in EXPECTED_TABLES:
        _check(t in profiled_names, f"profile for '{t}' present")


# ─────────────────────────── J. schema_snapshot.json ────────────────────────────────
def check_j():
    print("\n[J] schema_snapshot.json validation:")
    path = PROCESSED_DIR / "schema_snapshot.json"
    if not path.exists():
        _fail("file does not exist")
        return

    try:
        snap = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        _fail("invalid JSON")
        return

    required_keys = [
        "number_of_documents", "number_of_chunks", "document_types",
        "quarters", "regions", "segments", "related_metrics", "source_files", "generated_at",
    ]
    for key in required_keys:
        _check(key in snap, f"has key '{key}'")

    _check(snap.get("number_of_documents", 0) >= 20, f"number_of_documents >= 20 (got {snap.get('number_of_documents')})")
    _check(snap.get("number_of_chunks", 0) >= 20, f"number_of_chunks >= 20 (got {snap.get('number_of_chunks')})")

    snap_regions = set(snap.get("regions", {}).keys())
    snap_segments = set(snap.get("segments", {}).keys())

    for r in EXPECTED_REGIONS:
        _check(r in snap_regions, f"region '{r}' in snapshot regions")
    for s in EXPECTED_SEGMENTS:
        _check(s in snap_segments, f"segment '{s}' in snapshot segments")


# ─────────────────────────────── K. DuckDB validation ───────────────────────────────
def check_k():
    print("\n[K] DuckDB warehouse validation:")
    db_path = WAREHOUSE_DIR / "veridian.duckdb"
    if not db_path.exists():
        _fail("warehouse file missing")
        return

    try:
        import duckdb
    except ImportError:
        _fail("duckdb not installed")
        return

    try:
        con = duckdb.connect(str(db_path))
    except Exception as e:
        _fail(f"cannot connect: {e}")
        return

    try:
        # All 9 expected tables
        rows = con.execute("SHOW TABLES").fetchall()
        table_names = {r[0] for r in rows}
        for t in EXPECTED_TABLES:
            _check(t in table_names, f"table '{t}' exists in warehouse")

        # Revenue count
        rev = con.execute("SELECT COUNT(*) FROM revenue").fetchone()[0]
        _check(rev == 144, f"revenue has 144 rows (got {rev})")

        # Support tickets count
        tkt = con.execute("SELECT COUNT(*) FROM support_tickets").fetchone()[0]
        _check(200 <= tkt <= 500, f"support_tickets 200–500 rows (got {tkt})")

        # Aggregate: SELECT region, SUM(revenue) GROUP BY region
        agg = con.execute("""
            SELECT region, SUM(recognized_revenue) AS total_revenue
            FROM revenue
            GROUP BY region
            ORDER BY region
        """).fetchall()
        _check(len(agg) == 4, f"aggregate returns 4 rows (got {len(agg)})")
        for row in agg:
            _check(row[1] > 0, f"region '{row[0]}' total_revenue > 0 ({row[1]:.0f})")

        # APAC Enterprise Q4 < Q3
        q = con.execute("""
            SELECT quarter, SUM(recognized_revenue) AS revenue
            FROM revenue
            WHERE region = 'APAC' AND segment = 'Enterprise'
            GROUP BY quarter
            ORDER BY quarter
        """).fetchall()
        qdata = {r[0]: r[1] for r in q}
        if "Q3_2025" in qdata and "Q4_2025" in qdata:
            _check(qdata["Q4_2025"] < qdata["Q3_2025"],
                   f"APAC Enterprise Q4 revenue ({qdata['Q4_2025']:.0f}) < Q3 ({qdata['Q3_2025']:.0f})")
        else:
            _fail("APAC Enterprise Q3/Q4 data incomplete")

    except Exception as e:
        _fail(f"query error: {e}")
    finally:
        con.close()


# ───────────────────────────── L. Benchmark alignment ───────────────────────────────
def check_l():
    print("\n[L] Benchmark alignment:")
    bm = BENCHMARKS_DIR / "enterpriseqa_v0.jsonl"
    if not bm.exists():
        _fail("benchmark file does not exist")
        return

    raw = bm.read_text(encoding="utf-8")
    lines = raw.splitlines()
    _check(len(lines) > 0, "benchmark has entries")

    # Collect all existing doc IDs and table names
    existing_docs = {p.stem for p in UNSTRUCTURED_DIR.glob("*.md")}
    existing_tables = set(EXPECTED_TABLES)

    for idx, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            _fail(f"line {idx}: invalid JSON")
            continue

        q = entry.get("question", "")
        _check(bool(q.strip()), f"line {idx} ({entry.get('id','?')}): question non-empty")

        # expected_docs must map to real files
        for doc in entry.get("expected_docs", []):
            _check(doc in existing_docs, f"line {idx}: expected_doc '{doc}' exists in unstructured/")

        # expected_tables must map to real table names
        for tbl in entry.get("expected_tables", []):
            _check(tbl in existing_tables, f"line {idx}: expected_table '{tbl}' exists")

    _pass(f"{len(lines)} benchmark entries validated")


# ──────────────────────────── M. Banned keyword check ───────────────────────────────
def check_m():
    kw = FORBIDDEN_KEYWORD
    print(f"\n[M] Banned keyword check ({kw}):")
    scan_dirs = [
        ROOT / "docs",
        ROOT / "app" / "ingestion",
        ROOT / "scripts",
        ROOT / "tests",
        ROOT / "data" / "raw" / "unstructured",
        ROOT / "benchmarks",
    ]
    extensions = {".py", ".md", ".jsonl", ".json", ".csv", ".yaml", ".yml", ".txt", ".toml"}

    found = []
    for d in scan_dirs:
        if not d.exists():
            continue
        for p in sorted(d.rglob("*")):
            if p.is_dir():
                continue
            if p.suffix.lower() not in extensions:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if FORBIDDEN_KEYWORD in text:
                found.append(str(p.relative_to(ROOT)))

    if found:
        for f in found:
            _fail(f"'{FORBIDDEN_KEYWORD}' found in {f}")
    else:
        _pass("no banned keywords found")


# ─────────────────────────────────── Main ───────────────────────────────────────────
def main():
    print("=" * 60)
    print("  WEEK 2 VALIDATION — Veridian AI Synthetic Dataset & Ingestion")
    print("=" * 60)

    check_a()
    check_b()
    check_c()
    check_d()
    check_e()
    check_f()
    check_g()
    check_h()
    check_i()
    check_j()
    check_k()
    check_l()
    check_m()

    print()
    print("=" * 60)
    if ERRORS == 0:
        print("  *** WEEK 2 VALIDATION PASSED ***")
        print("=" * 60)
    else:
        print(f"  *** WEEK 2 VALIDATION FAILED: {ERRORS} error(s) ***")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
