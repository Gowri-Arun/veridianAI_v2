import pytest
from pathlib import Path
from app.ingestion.document_loader import load_documents, load_document

FORBIDDEN_KEYWORD = "Analyst" + "Graph"

def test_load_documents_success():
    unstructured_dir = Path("data/raw/unstructured")
    assert unstructured_dir.exists(), "Day 3 raw unstructured documents must exist"
    
    docs = load_documents(unstructured_dir)
    
    # Verify we loaded at least 20 documents
    assert len(docs) >= 20, f"Expected at least 20 documents, loaded {len(docs)}"
    
    # Verify each document has required fields
    for doc in docs:
        assert doc.doc_id, f"Document missing doc_id: {doc.source_path}"
        assert doc.title, f"Document missing title: {doc.source_path}"
        assert doc.doc_type, f"Document missing doc_type: {doc.source_path}"
        assert doc.text.strip(), f"Document text is empty: {doc.source_path}"
        assert doc.source_path, f"Document missing source_path: {doc.source_path}"
        assert isinstance(doc.metadata, dict), f"Document metadata is not a dict: {doc.source_path}"
        assert "related_metrics" in doc.metadata, f"related_metrics key missing in metadata: {doc.source_path}"
        assert isinstance(doc.metadata["related_metrics"], list), f"related_metrics is not a list: {doc.source_path}"
        
        # Verify no document contains restricted keyword
        assert FORBIDDEN_KEYWORD not in doc.text, f"Document {doc.doc_id} contains forbidden legacy keyword"
        assert FORBIDDEN_KEYWORD not in doc.title, f"Document {doc.doc_id} title contains forbidden legacy keyword"

def test_q4_apac_revenue_report_loads_correctly():
    target_path = Path("data/raw/unstructured/q4_apac_revenue_report.md")
    assert target_path.exists(), "q4_apac_revenue_report.md must exist in raw/unstructured"
    
    doc = load_document(target_path)
    
    assert doc.doc_id == "q4_apac_revenue_report"
    assert doc.title == "Q4 APAC Revenue Report"
    assert doc.doc_type == "regional_report"
    assert doc.text.strip(), "Document text must be non-empty"
    assert doc.source_path.endswith("q4_apac_revenue_report.md"), f"Expected source_path to end with q4_apac_revenue_report.md, got {doc.source_path}"
    assert "related_metrics" in doc.metadata
    assert doc.metadata["region"] == "APAC"
    assert doc.metadata["segment"] == "Enterprise"
    assert doc.metadata["quarter"] == "Q4_2025"
    assert "recognized_revenue" in doc.metadata["related_metrics"]
    assert "churn_rate" in doc.metadata["related_metrics"]

def test_load_document_malformed_frontmatter(tmp_path):
    # Unclosed frontmatter block
    content = """---
doc_id: broken_doc
title: Broken Doc
doc_type: test_doc
# Missing closing boundary
"""
    temp_file = tmp_path / "broken_doc.md"
    temp_file.write_text(content, encoding="utf-8")
    
    import pytest
    with pytest.raises(ValueError, match="frontmatter"):
        load_document(temp_file)

def test_load_document_empty_body(tmp_path):
    # Valid frontmatter, but empty body text
    content = """---
doc_id: empty_body_doc
title: Empty Body Doc
doc_type: test_doc
quarter: All
region: Global
segment: All
related_metrics:
  - recognized_revenue
source: unit_test
---
"""
    temp_file = tmp_path / "empty_body_doc.md"
    temp_file.write_text(content, encoding="utf-8")
    
    with pytest.raises(ValueError, match="empty"):
        load_document(temp_file)

def test_load_document_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_document("nonexistent_file.md")

def test_load_documents_directory_not_found():
    with pytest.raises(FileNotFoundError):
        load_documents("nonexistent_directory")

def test_load_documents_empty_directory(tmp_path):
    docs = load_documents(tmp_path)
    assert docs == []

def test_load_document_no_frontmatter(tmp_path):
    content = "# Just a heading\n\nSome body text without frontmatter."
    temp_file = tmp_path / "no_fm.md"
    temp_file.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required metadata field"):
        load_document(temp_file)

def test_load_document_partial_frontmatter(tmp_path):
    content = """---
doc_id: partial_doc
title: Partial Doc
# No doc_type, quarter, region, segment, related_metrics, or source
---
Body text here.
"""
    temp_file = tmp_path / "partial_doc.md"
    temp_file.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required metadata field"):
        load_document(temp_file)

def test_load_documents_skips_non_markdown(tmp_path):
    (tmp_path / "readme.txt").write_text("not a markdown file", encoding="utf-8")
    (tmp_path / "data.json").write_text('{"key": "value"}', encoding="utf-8")
    md_file = tmp_path / "real_doc.md"
    md_file.write_text("""---
doc_id: real_doc
title: Real Doc
doc_type: test_doc
quarter: Q1_2025
region: APAC
segment: SMB
related_metrics:
  - revenue
source: unit_test
---
Valid body.""", encoding="utf-8")
    docs = load_documents(tmp_path)
    assert len(docs) == 1
    assert docs[0].doc_id == "real_doc"

def test_load_document_preserves_absolute_source_path(tmp_path):
    content = """---
doc_id: abs_path_doc
title: Absolute Path Test
doc_type: test_doc
quarter: Q2_2025
region: EMEA
segment: Mid-Market
related_metrics:
  - bookings
source: unit_test
---
Body content.
"""
    temp_file = tmp_path / "abs_path_doc.md"
    temp_file.write_text(content, encoding="utf-8")
    doc = load_document(temp_file)
    expected = str(temp_file.resolve())
    assert doc.source_path == expected

def test_load_document_string_path_works():
    doc = load_document("data/raw/unstructured/q4_apac_revenue_report.md")
    assert doc.doc_id == "q4_apac_revenue_report"

def test_load_documents_returns_sorted_order():
    docs = load_documents("data/raw/unstructured")
    doc_ids = [d.doc_id for d in docs]
    assert doc_ids == sorted(doc_ids)
