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
    
    import pytest
    with pytest.raises(ValueError, match="empty"):
        load_document(temp_file)
